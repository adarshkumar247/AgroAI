"""AgroAI Dynamic Class-Label and Agronomic Taxonomy System.

Maps model output class indices and dataset folder names to certified botanical
pathology metadata, scientific binomials, severity ratings, and recovery protocols.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional

# Standard academic PlantVillage / Rice Leaf pathology reference metadata catalog
KNOWN_PATHOLOGY_METADATA: Dict[str, Dict[str, Any]] = {
    "Tomato___Early_blight": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Early Blight",
        "pathogen": "Alternaria solani",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Mild Spread",
        "spread_risk": "Moderate",
        "canopy_loss": "< 4%",
        "immediate_action": "Prune affected lower leaves, switch to targeted drip irrigation, apply clean straw mulch."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Late Blight",
        "pathogen": "Phytophthora infestans",
        "severity": "Critical Alert",
        "stage": "Stage 3 — Rapid Water-Soaked Lesions",
        "spread_risk": "High",
        "canopy_loss": "8 - 15%",
        "immediate_action": "Isolate affected sector immediately, remove infected foliage, apply authorized protective copper bio-fungicide."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Target Spot",
        "pathogen": "Corynespora cassiicola",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Concentric Rings",
        "spread_risk": "Moderate",
        "canopy_loss": "< 5%",
        "immediate_action": "Increase canopy spacing for cross-ventilation, avoid overhead irrigation during humid mornings."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Septoria Leaf Spot",
        "pathogen": "Septoria lycopersici",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Lower Foliage Flecks",
        "spread_risk": "Moderate",
        "canopy_loss": "< 4%",
        "immediate_action": "Prune lower infected canopy, sanitize pruning tools, avoid working among plants while foliage is wet."
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Leaf Mold",
        "pathogen": "Passalora fulva",
        "severity": "Moderate",
        "stage": "Stage 1 — Foliar Chlorosis",
        "spread_risk": "Moderate in High Humidity",
        "canopy_loss": "< 3%",
        "immediate_action": "Reduce polyhouse relative humidity below 80%, increase ventilation venting."
    },
    "Tomato___healthy": {
        "crop": "Tomato (Solanum lycopersicum)",
        "possible_issue": "Healthy Foliage",
        "pathogen": "None (No significant pathogen detected)",
        "severity": "Optimal Vigor",
        "stage": "Healthy Vegetative / Flowering",
        "spread_risk": "None / Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain balanced fertigation, support trellis structure, and continue routine visual scouting."
    },
    "Potato___Early_blight": {
        "crop": "Potato (Solanum tuberosum)",
        "possible_issue": "Potato Early Blight",
        "pathogen": "Alternaria solani",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Concentric Spots",
        "spread_risk": "Moderate",
        "canopy_loss": "< 5%",
        "immediate_action": "Ensure uniform soil moisture, avoid plant stress, apply certified protective foliar treatment."
    },
    "Potato___Late_blight": {
        "crop": "Potato (Solanum tuberosum)",
        "possible_issue": "Potato Late Blight",
        "pathogen": "Phytophthora infestans",
        "severity": "Critical Alert",
        "stage": "Stage 3 — Foliar & Stem Blight",
        "spread_risk": "High",
        "canopy_loss": "10 - 20%",
        "immediate_action": "Destroy infected haulms if tubers are mature, spray preventive contact fungicide, prevent water pooling."
    },
    "Potato___healthy": {
        "crop": "Potato (Solanum tuberosum)",
        "possible_issue": "Healthy Foliage",
        "pathogen": "None (No significant pathogen detected)",
        "severity": "Optimal Vigor",
        "stage": "Tuber Bulking Phase",
        "spread_risk": "None / Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain soil hilling, scout for Colorado beetle, and monitor soil moisture at 15cm."
    },
    "Corn___Common_rust": {
        "crop": "Maize / Corn (Zea mays)",
        "possible_issue": "Common Rust",
        "pathogen": "Puccinia sorghi",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Cinnamon Pustules",
        "spread_risk": "Moderate",
        "canopy_loss": "< 5%",
        "immediate_action": "Plant resistant hybrids in next rotation, monitor leaf pustules, avoid excessive nitrogen top-dressing."
    },
    "Corn___Common_rust_": {
        "crop": "Maize / Corn (Zea mays)",
        "possible_issue": "Common Rust",
        "pathogen": "Puccinia sorghi",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Cinnamon Pustules",
        "spread_risk": "Moderate",
        "canopy_loss": "< 5%",
        "immediate_action": "Plant resistant hybrids in next rotation, monitor leaf pustules, avoid excessive nitrogen top-dressing."
    },
    "Corn___Northern_Leaf_Blight": {
        "crop": "Maize / Corn (Zea mays)",
        "possible_issue": "Northern Corn Leaf Blight",
        "pathogen": "Exserohilum turcicum",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Cigar-Shaped Lesions",
        "spread_risk": "Moderate",
        "canopy_loss": "< 6%",
        "immediate_action": "Tillage to bury crop residue, practice 2-year crop rotation, scout upper canopy leaves during tasseling."
    },
    "Corn___healthy": {
        "crop": "Maize / Corn (Zea mays)",
        "possible_issue": "Healthy Foliage",
        "pathogen": "None (No significant pathogen detected)",
        "severity": "Optimal Vigor",
        "stage": "Vigor Vegetative Stand",
        "spread_risk": "None / Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain side-dress fertilizer schedule and weed control in inter-row alleys."
    },
    "Rice___Bacterial_blight": {
        "crop": "Paddy Rice (Oryza sativa)",
        "possible_issue": "Bacterial Blight",
        "pathogen": "Xanthomonas oryzae pv. oryzae",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Wavy Leaf Tip Necrosis",
        "spread_risk": "Moderate to High",
        "canopy_loss": "< 8%",
        "immediate_action": "Drain standing water for 48 hours to dry canopy, avoid excessive nitrogen, maintain balanced potassium."
    },
    "Rice___Brown_spot": {
        "crop": "Paddy Rice (Oryza sativa)",
        "possible_issue": "Brown Spot",
        "pathogen": "Bipolaris oryzae",
        "severity": "Attention Needed",
        "stage": "Stage 2 — Oval Brown Spots",
        "spread_risk": "Moderate",
        "canopy_loss": "< 5%",
        "immediate_action": "Test soil for silicon and potassium deficiency, ensure adequate water irrigation, avoid soil dryness."
    },
    "Rice___Leaf_blast": {
        "crop": "Paddy Rice (Oryza sativa)",
        "possible_issue": "Rice Blast",
        "pathogen": "Magnaporthe oryzae",
        "severity": "Critical Alert",
        "stage": "Stage 3 — Spindle-Shaped Lesions",
        "spread_risk": "High in Cool Nights",
        "canopy_loss": "10%",
        "immediate_action": "Apply certified blast-controlling foliar spray, withhold excess urea, maintain continuous flood layer."
    },
    "Rice___healthy": {
        "crop": "Paddy Rice (Oryza sativa)",
        "possible_issue": "Healthy Tillering Stage",
        "pathogen": "None (No significant pathogen detected)",
        "severity": "Optimal Vigor",
        "stage": "Vegetative Tillering",
        "spread_risk": "None / Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain 3-5cm standing water depth and continue scheduled nitrogen top-dressing."
    }
}

class DynamicClassManager:
    """Manages class mappings and translates model prediction indices to agronomic reports."""

    def __init__(self, classes_filepath: Optional[str] = None):
        self.class_names: List[str] = []
        if classes_filepath and os.path.exists(classes_filepath):
            self.load_classes(classes_filepath)
        else:
            # Default to reference PlantVillage core agricultural classes
            self.class_names = list(KNOWN_PATHOLOGY_METADATA.keys())

    def load_classes(self, filepath: str):
        """Load class labels dynamically from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                self.class_names = data
            elif isinstance(data, dict) and "classes" in data:
                self.class_names = data["classes"]

    def save_classes(self, filepath: str):
        """Persist class labels to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.class_names, f, indent=2)

    def get_metadata(self, class_name: str) -> Dict[str, Any]:
        """Dynamically resolve agronomic metadata for any class label."""
        if class_name in KNOWN_PATHOLOGY_METADATA:
            meta = KNOWN_PATHOLOGY_METADATA[class_name].copy()
            meta["raw_class"] = class_name
            return meta

        # Generic parsing fallback for novel classes: <Crop>___<Condition>
        parts = class_name.split("___")
        crop_part = parts[0].replace("_", " ").title() if len(parts) > 0 else "Unknown Crop"
        condition_part = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown Condition"

        is_healthy = "healthy" in condition_part.lower()

        return {
            "crop": crop_part,
            "possible_issue": condition_part if not is_healthy else "Healthy Foliage",
            "pathogen": "Scouted Pathogen" if not is_healthy else "None",
            "severity": "Optimal Vigor" if is_healthy else "Attention Needed",
            "stage": "Monitoring Stage",
            "spread_risk": "Low" if is_healthy else "Moderate",
            "canopy_loss": "0%" if is_healthy else "< 5%",
            "immediate_action": "Maintain standard agronomic scouting and soil water management.",
            "raw_class": class_name
        }

# Default singleton instance
class_manager = DynamicClassManager()
