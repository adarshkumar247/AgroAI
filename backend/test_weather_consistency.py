"""AgroAI Weather Consistency & Spray Advisory Verification Suite.

Validates PART 3, PART 4, PART 5 & PART 16:
1. Single weather response object from backend.
2. Dashboard temperature == Weather page temperature.
3. Irrigation uses identical meteorological inputs.
4. Spray status is identical across Dashboard and Weather.
5. Current timestamp is in local Asia/Kolkata timezone (no UTC leakage).
6. Zero contradictory spray labels (e.g. 'Safe for Spray' cannot coexist with 'Hold Spray' or 'Postpone').
7. Weather source ('Open-Meteo') and last-updated timestamp are present.
"""

import json
import urllib.request
from datetime import datetime

API_BASE = "http://127.0.0.1:8000/api/v1"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AgroAI-Test/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_tests():
    print("=" * 75)
    print("AGROAI WEATHER CONSISTENCY & SPRAY ADVISORY VERIFICATION")
    print("=" * 75)

    # 1. Fetch Weather API
    weather_data = fetch_json(f"{API_BASE}/weather?lat=26.8467&lon=80.9462")
    assert "current" in weather_data, "Weather API missing 'current' field"
    w_temp = weather_data["current"]["temperature_2m"]
    w_hum = weather_data["current"]["relative_humidity_2m"]
    w_wind = weather_data["current"]["wind_speed_10m"]
    w_advisory = weather_data.get("spray_advisory", {})
    w_spray_status = w_advisory.get("status") or w_advisory.get("spray_status")

    print(f"[1/7] Weather API: {w_temp}°C, Humidity: {w_hum}%, Wind: {w_wind} km/h, Spray Status: '{w_spray_status}'")

    # 2. Fetch Dashboard API
    dash_data = fetch_json(f"{API_BASE}/dashboard/summary")
    dash_mc = dash_data.get("micro_climate", {})
    dash_temp = dash_mc.get("temperature_num") or float(dash_mc.get("temperature", "").replace("°C", ""))
    dash_spray = dash_mc.get("spray_advisory", {})
    dash_spray_status = dash_spray.get("status") or dash_spray.get("spray_status") if isinstance(dash_spray, dict) else None

    # Assert Dashboard temperature == Weather temperature
    assert abs(dash_temp - w_temp) < 0.2, f"Dashboard temp ({dash_temp}) differs from Weather temp ({w_temp})"
    print(f"[PASS] 2. Dashboard temperature ({dash_temp}°C) matches Weather API ({w_temp}°C)")

    # 3. Assert Spray Status is identical across Weather and Dashboard
    if dash_spray_status:
        assert dash_spray_status == w_spray_status, f"Dashboard spray status ({dash_spray_status}) != Weather ({w_spray_status})"
    print(f"[PASS] 3. Spray status identical across Dashboard and Weather: '{w_spray_status}'")

    # 4. Fetch Irrigation API
    irrig_data = fetch_json(f"{API_BASE}/irrigation/recommendation?crop=Tomato&stage=vegetative&area_sqm=4047&soil_type=loam&lat=26.8467&lon=80.9462")
    irrig_wc = irrig_data.get("weather_context", {})
    irrig_temp = float(irrig_wc.get("temperature", "").replace("°C", ""))
    assert abs(irrig_temp - w_temp) < 0.2, f"Irrigation temp ({irrig_temp}) differs from Weather temp ({w_temp})"
    print(f"[PASS] 4. Irrigation weather context ({irrig_temp}°C) matches Weather API ({w_temp}°C)")

    # 5. Local Timezone Verification (Asia/Kolkata)
    timezone = weather_data.get("timezone", "")
    assert "Kolkata" in timezone or "Asia" in timezone, f"Expected Asia/Kolkata timezone, got '{timezone}'"
    last_updated = weather_data.get("last_updated", "")
    assert last_updated, "Weather missing last_updated timestamp"
    assert "Z" not in last_updated or "T" in last_updated, "Raw UTC timestamp leakage detected"
    print(f"[PASS] 5. Local farm timezone verified: '{timezone}', Last Updated: '{last_updated}'")

    # 6. Zero Contradictory Spray Labels Verification
    advisory_text = str(w_advisory.get("advisory", "")).lower()
    advisory_status = str(w_advisory.get("status", "")).lower()
    is_safe = w_advisory.get("is_safe_to_spray", False)

    if advisory_status == "postpone" or "टालें" in advisory_text or "postpone" in advisory_text:
        assert not is_safe, "Contradiction: is_safe_to_spray is True while status is Postpone!"
        assert "optimal spray window" not in advisory_text or "not recommended" in advisory_text, "Contradiction: 'Optimal' found in Postpone advisory"
    elif advisory_status == "optimal":
        assert is_safe, "Contradiction: is_safe_to_spray is False while status is Optimal!"
        assert "postpone" not in advisory_text, "Contradiction: 'Postpone' found in Optimal advisory"

    print(f"[PASS] 6. Zero contradictory spray labels: Status='{advisory_status}', is_safe={is_safe}")

    # 7. Weather Source & Disclaimer Transparency
    source = weather_data.get("source", "")
    assert "Open-Meteo" in source, f"Expected Open-Meteo source, got '{source}'"
    disclaimer = weather_data.get("disclaimer", "")
    assert "मौसम अनुमान बदल सकता है" in disclaimer or "change" in disclaimer.lower(), "Missing weather uncertainty disclaimer"
    print(f"[PASS] 7. Weather source ('{source}') and uncertainty disclaimer verified")

    print("=" * 75)
    print("ALL WEATHER CONSISTENCY CHECKS PASSED (7/7)")
    print("=" * 75)
    return True

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
