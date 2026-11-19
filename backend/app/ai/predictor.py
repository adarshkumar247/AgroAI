"""AgroAI Real PyTorch Inference Engine for Crop Disease Detection.

Executes MobileNetV3-Small forward inference on leaf imagery, evaluates confidence,
handles low-confidence / unknown specimens, and maps predictions to verified
agronomic pathology profiles for the FastAPI scanner endpoint and Stitch UI.
"""

import os
from typing import Optional, Dict, Any, List
import torch

# Keep inference predictable on small containers (Render Free has 0.1 CPU).
torch.set_num_threads(1)

from backend.app.ai.model import AgroDiseaseClassifier
from backend.app.ai.preprocessing import load_and_preprocess_image
from backend.app.ai.labels import class_manager

# Default model location
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
DEFAULT_WEIGHTS_PATH = os.path.join(MODEL_DIR, "best_model.pth")
CLASSES_JSON_PATH = os.path.join(MODEL_DIR, "classes.json")

class CropDiseasePredictor:
    """Production PyTorch MobileNetV3-Small inference engine."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or DEFAULT_WEIGHTS_PATH
        self.device = "cpu"
        self.model: Optional[AgroDiseaseClassifier] = None
        self.class_names: List[str] = []
        self.is_trained: bool = False
        self.confidence_threshold = 0.55

        self.load_model()

    def load_model(self):
        """Load trained weights or initialize pre-trained backbone."""
        if os.path.exists(self.model_path):
            try:
                print(f"[Predictor] Loading trained AgroAI weights from {self.model_path}...")
                self.model, self.class_names, metadata = AgroDiseaseClassifier.load_from_checkpoint(
                    filepath=self.model_path,
                    map_location=self.device
                )
                self.is_trained = True
                class_manager.class_names = self.class_names
                print(f"[Predictor] Successfully loaded model with {len(self.class_names)} classes.")
                return
            except Exception as e:
                print(f"[Predictor] Warning: Failed to load checkpoint ({e}). Initializing backbone.")

        # If checkpoint not trained yet or failed to load:
        # Dynamically load classes from classes.json if available
        if os.path.exists(CLASSES_JSON_PATH):
            class_manager.load_classes(CLASSES_JSON_PATH)

        self.class_names = class_manager.class_names
        num_classes = len(self.class_names)
        self.model = AgroDiseaseClassifier(num_classes=num_classes, pretrained=True)
        self.model.eval()
        self.model.to(self.device)
        self.is_trained = False
        print(f"[Predictor] MobileNetV3-Small backbone initialized with {num_classes} classes.")

    def reload_model(self, custom_path: Optional[str] = None):
        """Reload weights after a new training checkpoint is produced."""
        if custom_path:
            self.model_path = custom_path
        self.load_model()

    def predict(
        self,
        image_path: str,
        crop_hint: Optional[str] = None,
        symptoms: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform real PyTorch tensor inference on an input image.

        Args:
            image_path: Path to the stored image file.
            crop_hint: Optional user crop suggestion.
            symptoms: Optional noted symptoms.

        Returns:
            AgroAI diagnostic dictionary matching UI requirements.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        # 1. Preprocess image into normalized (1, 3, 224, 224) tensor
        input_tensor = load_and_preprocess_image(image_path)
        input_tensor = input_tensor.to(self.device)

        # 2. PyTorch Forward Pass
        self.model.eval()
        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = torch.softmax(logits, dim=1)[0]

        # 3. Extract Top Predictions
        k = min(3, len(self.class_names))
        top_probs, top_indices = torch.topk(probs, k=k)

        top_prob = float(top_probs[0].item())
        top_idx = int(top_indices[0].item())
        predicted_class = self.class_names[top_idx]

        top_candidates = []
        for p, idx in zip(top_probs, top_indices):
            top_candidates.append({
                "class": self.class_names[int(idx.item())],
                "confidence": round(float(p.item()), 4)
            })

        # 4. Unknown / Low Confidence Handling
        # If top probability falls below threshold, flag as uncertain rather than hallucinating
        if top_prob < self.confidence_threshold:
            return {
                "crop": "Unidentified Foliage / Specimen",
                "possible_issue": "Low Confidence Analysis (< 55%)",
                "confidence": round(top_prob, 2),
                "severity": "Uncertain Diagnosis",
                "stage": "Rescan Recommended",
                "pathogen": "Inconclusive (Blurry foliage, poor lighting, or unlisted species)",
                "spread_risk": "Unknown",
                "canopy_loss": "N/A",
                "immediate_action": "Capture a closer photo in bright natural light focusing directly on a single leaf blade against a neutral background.",
                "top_candidates": top_candidates,
                "model_version": "MobileNetV3-Small (PyTorch CPU)"
            }

        # 5. Resolve Rich Agronomic Pathology Metadata
        report = class_manager.get_metadata(predicted_class)
        report["confidence"] = round(top_prob, 2)
        report["top_candidates"] = top_candidates
        report["model_version"] = "MobileNetV3-Small (PyTorch CPU)"

        return report

# Global singleton predictor instance
predictor = CropDiseasePredictor()
