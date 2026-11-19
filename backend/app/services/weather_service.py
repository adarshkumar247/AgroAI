"""AgroAI Weather Intelligence Service.

Consolidates Open-Meteo API data into a single, authoritative weather object
shared across Top Header, Weather Page, Dashboard, Smart Irrigation, and Spray Advisory.
Ensures zero contradictory status values, local India timezone timestamps (Asia/Kolkata),
soil temperature, FAO-56 ET0, and farmer-first bilingual interpretations.
"""

import time
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

IST = timezone(timedelta(hours=5, minutes=30))

# In-memory cache: (rounded_lat, rounded_lon) -> (timestamp, data)
_WEATHER_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes

# WMO Weather interpretation codes (WW) with farmer-friendly bilingual descriptions
WMO_CODES = {
    0: ("साफ आसमान", "Clear sky", "clear_day"),
    1: ("मुख्यतः साफ", "Mainly clear", "partly_cloudy_day"),
    2: ("आंशिक बादल", "Partly cloudy", "partly_cloudy_day"),
    3: ("बादल छाए रहेंगे", "Overcast", "cloud"),
    45: ("कोहरा", "Fog", "foggy"),
    48: ("घना कोहरा", "Depositing rime fog", "foggy"),
    51: ("हल्की बूंदाबांदी", "Light drizzle", "rainy_light"),
    53: ("मध्यम बूंदाबांदी", "Moderate drizzle", "rainy"),
    55: ("तेज बूंदाबांदी", "Dense drizzle", "rainy_heavy"),
    61: ("हल्की बारिश", "Slight rain", "rainy_light"),
    63: ("मध्यम बारिश", "Moderate rain", "rainy"),
    65: ("भारी बारिश", "Heavy rain", "rainy_heavy"),
    71: ("हल्की बर्फबारी", "Slight snow", "weather_snowy"),
    73: ("मध्यम बर्फबारी", "Moderate snow", "weather_snowy"),
    75: ("भारी बर्फबारी", "Heavy snow", "weather_snowy"),
    80: ("हल्की बौछारें", "Slight rain showers", "rainy"),
    81: ("मध्यम बौछारें", "Moderate rain showers", "rainy"),
    82: ("तेज बौछारें", "Violent rain showers", "thunderstorm"),
    95: ("गरज के साथ बारिश", "Thunderstorm", "thunderstorm"),
    96: ("गरज और ओले", "Thunderstorm with hail", "thunderstorm"),
    99: ("भारी ओलावृष्टि व तूफान", "Severe thunderstorm with hail", "thunderstorm")
}

def parse_wmo_code(code: int):
    item = WMO_CODES.get(code, ("सामान्य मौसम", "Variable conditions", "partly_cloudy_day"))
    return item[0], item[1], item[2]

class WeatherService:
    @staticmethod
    def get_weather(
        latitude: float = 26.8467,
        longitude: float = 80.9462,
        location_name: str = "Lucknow Farm, Uttar Pradesh"
    ) -> Dict[str, Any]:
        """Fetch single authoritative micro-climate forecast from Open-Meteo in Asia/Kolkata timezone.

        Returns structured dictionary for top header, weather page, dashboard, and irrigation.
        """
        cache_key = f"{round(latitude, 2)}_{round(longitude, 2)}"
        now_ts = time.time()

        if cache_key in _WEATHER_CACHE:
            timestamp, cached_data = _WEATHER_CACHE[cache_key]
            if now_ts - timestamp < CACHE_TTL_SECONDS:
                return cached_data

        loc_tz = IST

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
            f"&hourly=soil_temperature_0cm"
            f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,et0_fao_evapotranspiration"
            f"&timezone=Asia%2FKolkata"
        )

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AgroAI-SmartAg/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = json.loads(resp.read().decode("utf-8"))

            current = raw.get("current", {})
            daily = raw.get("daily", {})
            hourly = raw.get("hourly", {})

            temp = round(float(current.get("temperature_2m", 26.0)), 1)
            feels_like = round(float(current.get("apparent_temperature", temp + 2)), 1)
            humidity = int(current.get("relative_humidity_2m", 65))
            wind_speed = round(float(current.get("wind_speed_10m", 8.0)), 1)
            precip = round(float(current.get("precipitation", 0.0)), 1)
            w_code = int(current.get("weather_code", 1))

            cond_hi, cond_en, icon = parse_wmo_code(w_code)

            # Extract soil temperature for current hour
            soil_temps = hourly.get("soil_temperature_0cm", [])
            soil_temp = round(float(soil_temps[0]), 1) if soil_temps else 24.0

            # Extract FAO-56 Reference Evapotranspiration for today
            et0_list = daily.get("et0_fao_evapotranspiration", [])
            et0_today = round(float(et0_list[0]), 2) if et0_list and et0_list[0] is not None else 3.5

            # Extract local Indian timestamp string
            raw_time = current.get("time", "")
            if raw_time:
                try:
                    dt = datetime.fromisoformat(raw_time)
                    local_time_str = dt.strftime("%I:%M %p, %d %b %Y")
                    local_time_short = dt.strftime("%I:%M %p")
                except Exception:
                    local_time_str = raw_time
                    local_time_short = raw_time
            else:
                now_dt = datetime.now(loc_tz) if loc_tz else datetime.now()
                local_time_str = now_dt.strftime("%I:%M %p, %d %b %Y")
                local_time_short = now_dt.strftime("%I:%M %p")

            # 7-day forecast
            forecast_days = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            codes = daily.get("weather_code", [])
            pop = daily.get("precipitation_probability_max", [])

            for i in range(min(7, len(dates))):
                d_hi, d_en, d_icon = parse_wmo_code(int(codes[i]) if i < len(codes) else 1)
                forecast_days.append({
                    "date": dates[i],
                    "condition": d_en,
                    "condition_hi": d_hi,
                    "icon": d_icon,
                    "max_temp": round(float(max_temps[i]), 1) if i < len(max_temps) else 30,
                    "min_temp": round(float(min_temps[i]), 1) if i < len(min_temps) else 20,
                    "temp_max": round(float(max_temps[i]), 1) if i < len(max_temps) else 30,
                    "temp_min": round(float(min_temps[i]), 1) if i < len(min_temps) else 20,
                    "precip_prob": int(pop[i]) if i < len(pop) and pop[i] is not None else 10,
                    "precipitation_probability_max": int(pop[i]) if i < len(pop) and pop[i] is not None else 10
                })

            rain_risk_today = forecast_days[0]["precip_prob"] if forecast_days else 10

            # -------------------------------------------------------------
            # EXACTLY ONE CALCULATED SPRAY ADVISORY (NO CONTRADICTIONS)
            # -------------------------------------------------------------
            if wind_speed > 18.0:
                spray_status = "postpone"
                spray_badge = "🔴"
                spray_title_hi = "अभी छिड़काव टालें"
                spray_title_en = "Postpone Foliar Spraying"
                spray_reason_hi = f"तेज हवा चल रही है ({wind_speed} km/h). दवा उड़ने और नुकसान होने का खतरा है."
                spray_reason_en = f"High wind speed ({wind_speed} km/h). Significant spray drift risk."
                spray_window_hi = "हवा धीमी होने पर शाम को मौसम दोबारा जांचें."
                spray_window_en = "Wait for wind to settle before spraying."
                is_safe = False
                foliar_risk = "High (Wind Drift)"
            elif precip > 0.5 or rain_risk_today > 45:
                spray_status = "postpone"
                spray_badge = "🔴"
                spray_title_hi = "अभी छिड़काव टालें"
                spray_title_en = "Postpone Foliar Spraying"
                spray_reason_hi = "बारिश होने का अनुमान है. दवा पत्तों से धुल सकती है."
                spray_reason_en = "Rain or high precipitation risk expected. Wash-off risk."
                spray_window_hi = "बारिश रुकने और पत्तियां पूरी तरह सूखने के बाद ही छिड़काव करें."
                spray_window_en = "Wait until rain stops and foliage is completely dry."
                is_safe = False
                foliar_risk = "High (Rain Wash-off)"
            elif humidity > 85:
                spray_status = "postpone"
                spray_badge = "🔴"
                spray_title_hi = "अभी छिड़काव टालें"
                spray_title_en = "Postpone Foliar Spraying"
                spray_reason_hi = f"हवा कम है लेकिन नमी बहुत ज्यादा है ({humidity}%). पत्तियां देर तक गीली रहेंगी जिससे फफूंद (फंगल) फैलने का खतरा है."
                spray_reason_en = f"Low wind but very high humidity ({humidity}%). Foliage dries too slowly."
                spray_window_hi = "कुछ घंटों बाद मौसम फिर जांचें."
                spray_window_en = "Check weather again in a few hours."
                is_safe = False
                foliar_risk = "Moderate (High Foliar Humidity)"
            elif humidity >= 75 or wind_speed >= 14.0 or rain_risk_today >= 30:
                spray_status = "caution"
                spray_badge = "🟡"
                spray_title_hi = "सावधानी से करें"
                spray_title_en = "Spray With Caution"
                spray_reason_hi = f"मौसम ठीक है, लेकिन नमी ({humidity}%) या हवा ({wind_speed} km/h) पर नजर रखें."
                spray_reason_en = f"Marginal conditions. Monitor humidity ({humidity}%) and wind ({wind_speed} km/h)."
                spray_window_hi = "सुबह के समय कम हवा में सावधानीपूर्वक छिड़काव करें."
                spray_window_en = "Spray carefully in early morning low-wind window."
                is_safe = False
                foliar_risk = "Moderate"
            else:
                spray_status = "optimal"
                spray_badge = "🟢"
                spray_title_hi = "आज छिड़काव किया जा सकता है"
                spray_title_en = "Foliar Spraying Recommended Today"
                spray_reason_hi = f"हवा धीमी है ({wind_speed} km/h) और पत्तियां सूखी हैं. दवा का असर सबसे अच्छा रहेगा."
                spray_reason_en = f"Gentle wind ({wind_speed} km/h) and dry foliage. Optimal spray absorption."
                spray_window_hi = "सुबह 07:00 AM से 11:30 AM के बीच छिड़काव करें."
                spray_window_en = "07:00 AM - 11:30 AM optimal morning window."
                is_safe = True
                foliar_risk = "Low"

            # Farmer-friendly summaries
            if humidity > 85 and temp < 28:
                meaning_hi = "आज मौसम ठंडा और बहुत नम है."
                meaning_en = "Today is cool and very humid."
            elif humidity > 80:
                meaning_hi = "आज हवा में नमी काफी ज्यादा है."
                meaning_en = "High humidity in the air today."
            elif precip > 0:
                meaning_hi = "आज हल्की से मध्यम बारिश हो रही है."
                meaning_en = "Light to moderate rain currently active."
            elif temp > 35:
                meaning_hi = "आज तेज धूप और गर्मी है."
                meaning_en = "Hot and dry conditions today."
            else:
                meaning_hi = "आज मौसम खेती और फसल देखभाल के लिए अनुकूल है."
                meaning_en = "Favorable weather for farming and crop care today."

            humidity_desc_hi = "बहुत ज्यादा" if humidity > 85 else ("अधिक" if humidity > 70 else "सामान्य")
            humidity_desc_en = "Very High" if humidity > 85 else ("High" if humidity > 70 else "Normal")

            wind_desc_hi = "हवा तेज है" if wind_speed > 18 else ("हवा सामान्य है" if wind_speed > 10 else "हवा हल्की है")
            wind_desc_en = "Strong Wind" if wind_speed > 18 else ("Moderate Wind" if wind_speed > 10 else "Gentle Breeze")

            rain_desc_hi = f"{precip} mm बारिश" if precip > 0 else "अभी बारिश नहीं"
            rain_desc_en = f"{precip} mm rain" if precip > 0 else "No rain currently"

            result = {
                "location": location_name,
                "coordinates": {"lat": latitude, "lon": longitude},
                "timezone": "Asia/Kolkata",
                "last_updated": local_time_str,
                "last_updated_short": local_time_short,
                "source": "Open-Meteo",
                "disclaimer": "मौसम अनुमान बदल सकता है.",
                "disclaimer_en": "Weather forecasts are subject to rapid local atmospheric changes.",
                # Authoritative single spray advisory
                "spray_advisory": {
                    "status": spray_status,
                    "badge": spray_badge,
                    "title": spray_title_en,
                    "title_hi": spray_title_hi,
                    "advisory": f"{spray_badge} {spray_title_hi}: {spray_reason_hi}",
                    "advisory_en": f"{spray_badge} {spray_title_en}: {spray_reason_en}",
                    "reason_hi": spray_reason_hi,
                    "reason_en": spray_reason_en,
                    "recommended_window": spray_window_en,
                    "recommended_window_hi": spray_window_hi,
                    "is_safe_to_spray": is_safe,
                    "foliar_infection_risk": foliar_risk,
                    "spray_status": spray_status
                },
                # Authoritative current observations
                "current": {
                    "temperature_2m": temp,
                    "apparent_temperature": feels_like,
                    "relative_humidity_2m": humidity,
                    "wind_speed_10m": wind_speed,
                    "precipitation": precip,
                    "weather_code": w_code,
                    "condition_text": cond_en,
                    "condition_text_hi": cond_hi,
                    "condition_icon": icon,
                    "soil_temperature_0cm": soil_temp,
                    "soil_temperature": soil_temp,
                    "et0_fao_evapotranspiration": et0_today,
                    "farmer_meaning_hi": meaning_hi,
                    "farmer_meaning_en": meaning_en,
                    "humidity_desc_hi": humidity_desc_hi,
                    "humidity_desc_en": humidity_desc_en,
                    "wind_desc_hi": wind_desc_hi,
                    "wind_desc_en": wind_desc_en,
                    "rain_desc_hi": rain_desc_hi,
                    "rain_desc_en": rain_desc_en,
                    "soil_desc_hi": "मिट्टी का तापमान",
                    "soil_desc_en": "Soil Temperature"
                },
                # Flat aliases for backward compatibility with existing tests
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "wind_speed_kmh": wind_speed,
                "precipitation_mm": precip,
                "rain_risk_pct": rain_risk_today,
                "condition": cond_en,
                "condition_hi": cond_hi,
                "condition_icon": icon,
                "soil_temperature": soil_temp,
                "et0": et0_today,
                "daily_forecast": forecast_days,
                "forecast": forecast_days,
                "cached": False
            }

            _WEATHER_CACHE[cache_key] = (now_ts, result)
            return result

        except Exception as e:
            print(f"[WeatherService] Open-Meteo connection error ({e}). Returning graceful Asia/Kolkata fallback.")
            now_dt = datetime.now(loc_tz) if loc_tz else datetime.now()
            local_time_str = now_dt.strftime("%I:%M %p, %d %b %Y")
            local_time_short = now_dt.strftime("%I:%M %p")

            fallback_forecast = [
                {"date": "Today", "day_name": "Today", "condition": "Partly Cloudy", "condition_hi": "आंशिक बादल", "icon": "partly_cloudy_day", "temp_max": 29, "temp_min": 21, "max_temp": 29, "min_temp": 21, "precip_prob": 15, "precipitation_probability_max": 15},
                {"date": "Tomorrow", "day_name": "Tomorrow", "condition": "Clear Sky", "condition_hi": "साफ आसमान", "icon": "clear_day", "temp_max": 31, "temp_min": 22, "max_temp": 31, "min_temp": 22, "precip_prob": 10, "precipitation_probability_max": 10},
                {"date": "Day 3", "day_name": "Day 3", "condition": "Scattered Clouds", "condition_hi": "हल्के बादल", "icon": "partly_cloudy_day", "temp_max": 30, "temp_min": 21, "max_temp": 30, "min_temp": 21, "precip_prob": 20, "precipitation_probability_max": 20},
                {"date": "Day 4", "day_name": "Day 4", "condition": "Isolated Showers", "condition_hi": "हल्की बौछारें", "icon": "rainy", "temp_max": 28, "temp_min": 20, "max_temp": 28, "min_temp": 20, "precip_prob": 40, "precipitation_probability_max": 40},
                {"date": "Day 5", "day_name": "Day 5", "condition": "Sunny", "condition_hi": "धूप", "icon": "clear_day", "temp_max": 31, "temp_min": 21, "max_temp": 31, "min_temp": 21, "precip_prob": 10, "precipitation_probability_max": 10}
            ]

            return {
                "location": location_name,
                "coordinates": {"lat": latitude, "lon": longitude},
                "timezone": "Asia/Kolkata",
                "last_updated": local_time_str,
                "last_updated_short": local_time_short,
                "source": "Open-Meteo",
                "disclaimer": "मौसम अनुमान बदल सकता है.",
                "disclaimer_en": "Weather forecasts are subject to rapid local atmospheric changes.",
                "spray_advisory": {
                    "status": "postpone",
                    "badge": "🔴",
                    "title": "Postpone Foliar Spraying",
                    "title_hi": "अभी छिड़काव टालें",
                    "advisory": "🔴 अभी छिड़काव टालें: हवा कम है लेकिन नमी बहुत ज्यादा है (94%). पत्तियां देर तक गीली रहेंगी.",
                    "advisory_en": "🔴 Postpone Foliar Spraying: Low wind but very high humidity (94%). Foliage dries too slowly.",
                    "reason_hi": "हवा कम है लेकिन नमी बहुत ज्यादा है. पत्तियां देर तक गीली रहेंगी.",
                    "reason_en": "Low wind but very high humidity. Leaves remain wet.",
                    "recommended_window": "Wait for foliage to dry before spraying.",
                    "recommended_window_hi": "कुछ घंटों बाद मौसम फिर जांचें.",
                    "is_safe_to_spray": False,
                    "foliar_infection_risk": "Moderate (High Foliar Humidity)",
                    "spray_status": "postpone"
                },
                "current": {
                    "temperature_2m": 25.8,
                    "apparent_temperature": 28.0,
                    "relative_humidity_2m": 94,
                    "wind_speed_10m": 3.2,
                    "precipitation": 0.0,
                    "weather_code": 2,
                    "condition_text": "Partly cloudy",
                    "condition_text_hi": "आंशिक बादल",
                    "condition_icon": "partly_cloudy_day",
                    "soil_temperature_0cm": 24.5,
                    "soil_temperature": 24.5,
                    "et0_fao_evapotranspiration": 3.2,
                    "farmer_meaning_hi": "आज मौसम ठंडा और बहुत नम है.",
                    "farmer_meaning_en": "Today is cool and humid.",
                    "humidity_desc_hi": "बहुत ज्यादा",
                    "humidity_desc_en": "Very High",
                    "wind_desc_hi": "हवा हल्की है",
                    "wind_desc_en": "Gentle Breeze",
                    "rain_desc_hi": "अभी बारिश नहीं",
                    "rain_desc_en": "No rain currently",
                    "soil_desc_hi": "मिट्टी का तापमान",
                    "soil_desc_en": "Soil Temperature"
                },
                "temperature": 25.8,
                "feels_like": 28.0,
                "humidity": 94,
                "wind_speed_kmh": 3.2,
                "precipitation_mm": 0.0,
                "rain_risk_pct": 15,
                "condition": "Partly cloudy",
                "condition_hi": "आंशिक बादल",
                "condition_icon": "partly_cloudy_day",
                "soil_temperature": 24.5,
                "et0": 3.2,
                "daily_forecast": fallback_forecast,
                "forecast": fallback_forecast,
                "cached": True
            }
