from typing import Optional
from fastapi import APIRouter, Query
from backend.app.services.irrigation_service import IrrigationService

router = APIRouter()

@router.get("/recommendation")
def get_irrigation_recommendation(
    crop: str = Query("Tomato", description="Crop species"),
    stage: str = Query("Vegetative", description="Growth stage: Initial, Vegetative, Mid, Late"),
    soil: str = Query("Alluvial", description="Soil texture type"),
    area_sqm: float = Query(4047.0, description="Field area in square meters (default: 1 acre)"),
    method: str = Query("Drip", description="Irrigation method: Drip, Sprinkler, Flood"),
    user_moisture: Optional[float] = Query(None, description="Optional manual field moisture measurement percentage"),
    lat: float = Query(26.8467, description="Latitude (default: Lucknow, UP)"),
    lon: float = Query(80.9462, description="Longitude (default: Lucknow, UP)")
):
    """Calculate FAO-56 crop evapotranspiration, recommended water volume, and valve schedule."""
    return IrrigationService.calculate_irrigation(
        crop=crop,
        growth_stage=stage,
        soil_type=soil,
        field_area_sqm=area_sqm,
        irrigation_method=method,
        user_soil_moisture_pct=user_moisture,
        lat=lat,
        lon=lon
    )

