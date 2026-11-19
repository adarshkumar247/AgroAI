"""AgroAI Crop Identification Service.

Reuses the trained PyTorch MobileNetV3-Small computer-vision model to classify
botanical crop species and families from leaf imagery.
Gracefully and clearly reports unsupported or low-confidence specimens.
"""

import os
import torch
from typing import Dict, Any, Optional
from backend.app.ai.predictor import predictor
from backend.app.ai.preprocessing import load_and_preprocess_image

# Botanical and Agronomic Species Catalog
BOTANICAL_CATALOG = {
    "tomato": {
        "common_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "botanical_family": "Solanaceae (Nightshade Family)",
        "growing_season": "Warm-season annual (Kharif / Rabi / Zaid in frost-free regions)",
        "soil_preference": "Well-drained sandy loam to clay loam, pH 6.0 - 6.8",
        "water_requirement": "400 - 600 mm per crop cycle (moderate, sensitive to waterlogging)",
        "common_cultivars": ["Pusa Ruby", "Roma VF", "Arka Vikas", "Himsona", "San Marzano"],
        "companion_plants": ["Basil", "Marigold (nematode deterrent)", "Garlic"]
    },
    "potato": {
        "common_name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "botanical_family": "Solanaceae (Nightshade Family)",
        "growing_season": "Cool-season tuber crop (Winter / Rabi)",
        "soil_preference": "Friable, loose, well-aerated sandy loam, pH 5.2 - 6.5",
        "water_requirement": "500 - 700 mm per crop cycle (high water need during tuber bulking)",
        "common_cultivars": ["Kufri Jyoti", "Kufri Pukhraj", "Kufri Bahar", "Russet Burbank"],
        "companion_plants": ["Beans", "Cabbage", "Corn", "Horseradish"]
    },
    "corn": {
        "common_name": "Maize / Corn",
        "scientific_name": "Zea mays",
        "botanical_family": "Poaceae / Gramineae (Grass Family)",
        "growing_season": "Warm-season cereal (Kharif / Spring-Summer)",
        "soil_preference": "Deep, fertile, well-drained silt loam to clay loam, pH 6.0 - 7.5",
        "water_requirement": "500 - 800 mm per crop cycle (critical during tasseling and silking)",
        "common_cultivars": ["DeKalb 9108", "Ganga Safed 2", "Pioneer 30V92", "African Tall"],
        "companion_plants": ["Climbing Beans (Three Sisters system)", "Squash / Pumpkin"]
    },
    "rice": {
        "common_name": "Paddy Rice",
        "scientific_name": "Oryza sativa",
        "botanical_family": "Poaceae / Gramineae (Grass Family)",
        "growing_season": "Wet-season tropical cereal (Kharif / Aman / Boro)",
        "soil_preference": "Heavy clay to alluvial silt soils with high water retention capacity, pH 5.5 - 6.8",
        "water_requirement": "1100 - 1500 mm per cycle (requires standing water during tillering)",
        "common_cultivars": ["Basmati 370", "Pusa 1121", "Swarna (MTU 7029)", "IR 64", "BPT 5204"],
        "companion_plants": ["Azolla (bio-fertilizer nitrogen fixer)", "Duckweed"]
    }
}

class CropIdService:
    @staticmethod
    def identify_crop(image_path: str) -> Dict[str, Any]:
        """Perform botanical classification on a foliage photo using MobileNetV3-Small."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        # Preprocess input tensor
        tensor = load_and_preprocess_image(image_path)
        tensor = tensor.to(predictor.device)

        # Forward pass through MobileNetV3-Small
        predictor.model.eval()
        with torch.no_grad():
            logits = predictor.model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        # Aggregate class probabilities by species
        species_scores = {"tomato": 0.0, "potato": 0.0, "corn": 0.0, "rice": 0.0}

        for idx, class_name in enumerate(predictor.class_names):
            p = float(probs[idx].item())
            c_lower = class_name.lower()
            if "tomato" in c_lower:
                species_scores["tomato"] += p
            elif "potato" in c_lower:
                species_scores["potato"] += p
            elif "corn" in c_lower or "maize" in c_lower:
                species_scores["corn"] += p
            elif "rice" in c_lower:
                species_scores["rice"] += p

        # Sort species by aggregated confidence
        sorted_species = sorted(species_scores.items(), key=lambda x: x[1], reverse=True)
        top_species, top_score = sorted_species[0]

        # Uncertainty handling: If confidence is below 50%
        if top_score < 0.50:
            return {
                "identified": False,
                "supported": False,
                "crop": None,
                "common_name": "Unidentified / Unsupported Crop Species",
                "botanical_name": "Inconclusive (Non-cataloged species or low-quality photo)",
                "scientific_name": "Inconclusive (Non-cataloged species or low-quality photo)",
                "family": "Unverified Botanical Family",
                "botanical_family": "Unverified Botanical Family",
                "confidence": round(top_score, 2),
                "severity_badge": "Uncertain Identification",
                "message": "The AgroAI computer-vision model currently specializes in Solanaceae (Tomato, Potato) and Poaceae (Paddy Rice, Maize). The uploaded specimen does not meet the confidence threshold. Please take a clearer, top-down photo of a single leaf blade in natural daylight.",
                "advisory": "The AgroAI computer-vision model currently specializes in Solanaceae (Tomato, Potato) and Poaceae (Paddy Rice, Maize). The uploaded specimen does not meet the confidence threshold. Please take a clearer, top-down photo of a single leaf blade in natural daylight.",
                "candidate_species": [
                    {"species": BOTANICAL_CATALOG[s]["common_name"], "confidence": round(sc, 4)}
                    for s, sc in sorted_species
                ],
                "model_architecture": "MobileNetV3-Small (PyTorch CPU)"
            }

        # Confident botanical match
        info = BOTANICAL_CATALOG[top_species]
        return {
            "identified": True,
            "supported": True,
            "crop": info["common_name"],
            "common_name": info["common_name"],
            "botanical_name": info["scientific_name"],
            "scientific_name": info["scientific_name"],
            "family": info["botanical_family"],
            "botanical_family": info["botanical_family"],
            "confidence": round(top_score, 2),
            "severity_badge": "High Confidence Match",
            "growing_season": info["growing_season"],
            "soil_preference": info["soil_preference"],
            "water_requirement": info["water_requirement"],
            "common_cultivars": info["common_cultivars"],
            "companion_plants": info["companion_plants"],
            "candidate_species": [
                {"species": BOTANICAL_CATALOG[s]["common_name"], "confidence": round(sc, 4)}
                for s, sc in sorted_species
            ],
            "model_architecture": "MobileNetV3-Small (PyTorch CPU)"
        }
