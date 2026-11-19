from typing import Optional
from fastapi import APIRouter, Query
from backend.app.services.nutrient_service import NutrientService

router = APIRouter()

@router.get("/guidance")
def get_nutrient_guidance(
    crop: str = Query("Tomato", description="Crop species"),
    soil: str = Query("Alluvial", description="Soil texture type"),
    symptom: Optional[str] = Query(None, description="Observed foliar symptom: lower_leaf_yellowing, purpling_leaves, leaf_edge_scorch, blossom_end_rot, interveinal_chlorosis"),
    observed_symptoms: Optional[str] = Query(None, description="Alias for symptom (alternate query key)"),
    stage: Optional[str] = Query("vegetative", description="Crop growth stage"),
    soil_ph: Optional[float] = Query(None, description="Observed soil pH value"),
    area_sqm: float = Query(4047.0, description="Field area in square meters (default: 1 acre)")
):
    """Diagnose nutrient deficiencies and generate advisory fertilizer and organic compost schedules."""
    effective_symptom = symptom or observed_symptoms
    return NutrientService.get_recommendation(
        crop=crop,
        soil_type=soil,
        observed_symptom=effective_symptom,
        field_area_sqm=area_sqm,
        growth_stage=stage or "vegetative",
        soil_ph=soil_ph
    )

