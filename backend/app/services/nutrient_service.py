"""AgroAI Nutrient & Fertilizer Guidance Service.

Provides transparent agronomic soil fertility and deficiency diagnosis based on
foliar visual indicators, university extension standards, and crop extraction curves.
Does not present chemical dosages as guaranteed prescriptions; includes explicit
advisory disclaimers and organic alternatives for every recommendation.
"""

from typing import Dict, Any, List, Optional

# Standard Recommended Dose of Fertilizers (RDF in kg/ha: N - P2O5 - K2O)
STANDARD_RDF = {
    "tomato": {"n": 120, "p": 60, "k": 60, "ph_optimal": "6.0 - 6.8"},
    "potato": {"n": 150, "p": 100, "k": 100, "ph_optimal": "5.5 - 6.5"},
    "maize": {"n": 120, "p": 60, "k": 40, "ph_optimal": "6.0 - 7.5"},
    "corn": {"n": 120, "p": 60, "k": 40, "ph_optimal": "6.0 - 7.5"},
    "rice": {"n": 100, "p": 50, "k": 50, "ph_optimal": "5.5 - 6.5"},
    "wheat": {"n": 120, "p": 60, "k": 40, "ph_optimal": "6.0 - 7.5"}
}

# Foliar symptom deficiency rules
DEFICIENCY_CATALOG = {
    "lower_leaf_yellowing": {
        "element": "Nitrogen (N)",
        "role": "Chlorophyll synthesis and vegetative biomass growth",
        "severity": "Moderate Deficit",
        "symptoms": "Uniform yellowing (chlorosis) beginning on older lower foliage while upper growth remains pale green.",
        "organic_remedy": "Apply well-composted vermicompost (2-3 tonnes/ha) or liquid fermented neem-cow dung slurry (Jeevamrutha).",
        "synthetic_option": "Foliar spray of 1% water-soluble Urea (10g/L water) or side-dress 25 kg/ha Urea at active tillering.",
        "split_schedule": "Apply nitrogen in 3 split doses (basal, vegetative, flowering) to reduce leaching."
    },
    "purpling_leaves": {
        "element": "Phosphorus (P)",
        "role": "Root development, energy transfer (ATP), and early flowering",
        "severity": "Attention Needed",
        "symptoms": "Dark green foliage with distinct purple or reddish-bronze pigmentation on leaf undersides and stems.",
        "organic_remedy": "Incorporate steamed bone meal or rock phosphate (100 kg/ha) along with phosphate solubilizing bacteria (PSB).",
        "synthetic_option": "Apply Di-Ammonium Phosphate (DAP) or Single Super Phosphate (SSP) placed 5cm beneath seed depth.",
        "split_schedule": "Apply 100% of phosphorus as basal dressing before transplanting."
    },
    "leaf_edge_scorch": {
        "element": "Potassium (K)",
        "role": "Stomatal regulation, disease resistance, and fruit/tuber filling",
        "severity": "Attention Needed",
        "symptoms": "Marginal chlorosis followed by dry brown scorching/necrosis along the outer leaf tips and edges.",
        "organic_remedy": "Apply sifted hardwood ash (50 kg/ha) or fermented banana pseudostem bio-potash.",
        "synthetic_option": "Apply Muriate of Potash (MOP / KCl) or Sulfate of Potash (SOP / K2SO4) at 30-40 kg/ha.",
        "split_schedule": "Split 50% basal and 50% during fruit/panicle swelling stage."
    },
    "blossom_end_rot": {
        "element": "Calcium (Ca)",
        "role": "Cell wall pectate integrity and apical bud development",
        "severity": "High Vulnerability",
        "symptoms": "Water-soaked dark sunken black rot at the blossom end of fruits (tomatoes/peppers) or curled leaf margins.",
        "organic_remedy": "Incorporate agricultural gypsum or crushed eggshell powder (200 kg/ha) into root zone.",
        "synthetic_option": "Foliar application of Calcium Nitrate (1.5g/L) during active fruit expansion.",
        "split_schedule": "Maintain consistent soil moisture; irregular watering inhibits calcium uptake regardless of soil content."
    },
    "interveinal_chlorosis": {
        "element": "Magnesium (Mg) / Micronutrients",
        "role": "Central atom of chlorophyll ring",
        "severity": "Mild Deficit",
        "symptoms": "Yellowing between veins while leaf veins remain distinctly green (herringbone pattern).",
        "organic_remedy": "Foliar application of Epsom salt (Magnesium Sulfate) at 5g/L or seaweed extract bio-stimulant.",
        "synthetic_option": "Apply chelated micronutrient mixture (Grade 2) as foliar mist.",
        "split_schedule": "Spray twice: once at early vegetative stage, once at pre-flowering."
    }
}

class NutrientService:
    @staticmethod
    def get_recommendation(
        crop: str = "tomato",
        soil_type: str = "alluvial",
        observed_symptom: Optional[str] = None,
        field_area_sqm: float = 4047.0,  # 1 Acre
        growth_stage: str = "vegetative",
        soil_ph: Optional[float] = None
    ) -> Dict[str, Any]:
        """Compute transparent agronomic nutrient plan with both organic and synthetic options."""
        crop_clean = crop.lower().strip()
        crop_key = next((k for k in STANDARD_RDF if k in crop_clean), "tomato")
        rdf = STANDARD_RDF[crop_key]

        hectares = field_area_sqm / 10000.0
        acres = round(field_area_sqm / 4046.86, 2)

        # Base requirement for area
        base_n = round(rdf["n"] * hectares, 1)
        base_p = round(rdf["p"] * hectares, 1)
        base_k = round(rdf["k"] * hectares, 1)

        # Diagnose symptom
        symptom_key = (observed_symptom or "").lower().strip()
        matched_deficiency = DEFICIENCY_CATALOG.get(symptom_key)

        if not matched_deficiency:
            # Standard balanced maintenance
            diagnosis_label = "Balanced Crop Nutrient Maintenance"
            primary_deficiency = "None (Routine Maintenance)"
            actions = {
                "organic_solution": "Incorporate 2-3 tonnes of farmyard manure (FYM) or 500 kg vermicompost per acre before planting.",
                "synthetic_solution": f"Apply {base_n} kg N, {base_p} kg P2O5, and {base_k} kg K2O per acre split across 3 growth phases.",
                "timing": "Basal application prior to planting, top-dress at 30 and 60 days."
            }
            severity = "Optimal Vigor"
            deficiency_cause = "No specific foliar symptom reported. Routine balanced nutrient maintenance recommended."
            deficiency_confidence = 1.0
        else:
            diagnosis_label = f"Suspected {matched_deficiency['element']} Deficiency"
            primary_deficiency = matched_deficiency['element']
            actions = {
                "organic_solution": matched_deficiency["organic_remedy"],
                "synthetic_solution": matched_deficiency["synthetic_option"],
                "timing": matched_deficiency["split_schedule"]
            }
            severity = matched_deficiency["severity"]
            deficiency_cause = matched_deficiency["symptoms"]
            deficiency_confidence = 0.88

        # Effective soil pH
        effective_ph = soil_ph if soil_ph is not None else None
        ph_display = str(effective_ph) if effective_ph is not None else rdf["ph_optimal"]

        return {
            "crop": crop.title(),
            "soil_type": soil_type.title(),
            "growth_stage": growth_stage.title() if growth_stage else "Vegetative",
            "field_area_acres": acres,
            "soil_ph": effective_ph if effective_ph is not None else 6.8,
            "optimal_soil_ph": rdf["ph_optimal"],
            "diagnosis": {
                "detected_deficiency": primary_deficiency,
                "confidence": deficiency_confidence,
                "cause": deficiency_cause,
                "severity": severity,
                "label": diagnosis_label
            },
            "primary_deficiency": primary_deficiency,
            "severity": severity,
            "symptom_observed": observed_symptom or "Routine Farm Health Check",
            "standard_npk_rdf_kg_per_ha": {
                "nitrogen_n": rdf["n"],
                "phosphorus_p2o5": rdf["p"],
                "potassium_k2o": rdf["k"]
            },
            "base_crop_rdf_kg_ha": {
                "nitrogen_n": rdf["n"],
                "phosphorus_p2o5": rdf["p"],
                "potassium_k2o": rdf["k"]
            },
            "field_requirement_kg": {
                "nitrogen_n": base_n,
                "phosphorus_p2o5": base_p,
                "potassium_k2o": base_k
            },
            "recommendations": {
                "synthetic_option": actions["synthetic_solution"],
                "organic_option": actions["organic_solution"],
                "foliar_intervention": matched_deficiency["synthetic_option"] if matched_deficiency else f"Foliar spray of 1% water-soluble Urea (10g/L) during cool morning hours.",
                "application_timing": actions["timing"]
            },
            "prescribed_solutions": actions,
            "disclaimer": "These values are indicative agronomic baselines derived from ICAR recommended dose of fertilizer (RDF) standards and university agricultural extension foliar symptom mapping. They do not substitute a certified laboratory soil test. Always consult a licensed agronomist before large-scale chemical fertilizer application."
        }

