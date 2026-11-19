from typing import Optional
from fastapi import APIRouter, Query
from backend.app.services.weather_service import WeatherService

router = APIRouter()

@router.get("")
def get_weather(
    lat: float = Query(26.8467, description="Latitude (default: Lucknow, UP)"),
    lon: float = Query(80.9462, description="Longitude (default: Lucknow, UP)"),
    location: str = Query("Lucknow Farm, Uttar Pradesh", description="Display location name")
):
    """Retrieve micro-climate telemetry, 7-day forecast, and foliar spray advisories."""
    return WeatherService.get_weather(latitude=lat, longitude=lon, location_name=location)

@router.get("/current")
def get_current_weather(
    lat: float = Query(26.8467, description="Latitude (default: Lucknow, UP)"),
    lon: float = Query(80.9462, description="Longitude (default: Lucknow, UP)"),
    location: str = Query("Lucknow Farm, Uttar Pradesh", description="Display location name")
):
    """Retrieve simplified current weather metrics for header bar."""
    weather = WeatherService.get_weather(latitude=lat, longitude=lon, location_name=location)
    cur = weather.get("current", {})
    spray = weather.get("spray_advisory", {})
    return {
        "temperature_c": cur.get("temperature_2m"),
        "temperature": f"{cur.get('temperature_2m')}°C",
        "condition_hi": cur.get("condition_hi"),
        "condition_en": cur.get("condition_text"),
        "condition": cur.get("condition_hi") or cur.get("condition_text"),
        "humidity": f"{cur.get('relative_humidity_2m')}%",
        "wind_speed": f"{cur.get('wind_speed_10m')} km/h",
        "spray_advisory": spray,
        "location": location
    }
