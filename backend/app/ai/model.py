"""AgroAI PyTorch MobileNetV3-Small Neural Architecture for Crop Disease Classification.

Designed for lightweight, CPU-efficient edge inference and transfer learning.
"""

import os
from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

class AgroDiseaseClassifier(nn.Module):
    """MobileNetV3-Small architecture adapted for multi-crop plant pathology."""

    def __init__(
        self,
        num_classes: int,
        pretrained: bool = True,
        dropout: float = 0.2
    ):
        super().__init__()
        self.num_classes = num_classes

        # Load MobileNetV3-Small backbone
        weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        try:
            self.backbone = mobilenet_v3_small(weights=weights)
        except Exception:
            # Fallback if offline / weights unavailable
            self.backbone = mobilenet_v3_small(weights=None)

        in_features = self.backbone.classifier[0].in_features  # 576 for mobilenet_v3_small

        # Replace classification head with custom agricultural classifier
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, 1024),
            nn.Hardswish(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(1024, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning unnormalized class logits.
        
        Args:
            x: Tensor of shape (Batch_Size, 3, 224, 224)
        """
        return self.backbone(x)

    def freeze_backbone(self, freeze: bool = True):
        """Freeze backbone convolutional feature extractor for initial transfer learning."""
        for name, param in self.backbone.features.named_parameters():
            param.requires_grad = not freeze

    def unfreeze_head(self):
        """Ensure classifier head parameters are always trainable."""
        for param in self.backbone.classifier.parameters():
            param.requires_grad = True

    def save_checkpoint(
        self,
        filepath: str,
        class_names: list,
        epoch: int = 0,
        val_acc: float = 0.0,
        val_loss: float = 0.0,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        """Save model state dictionary along with class labels and training telemetry."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        checkpoint = {
            "num_classes": self.num_classes,
            "class_names": class_names,
            "state_dict": self.state_dict(),
            "epoch": epoch,
            "val_acc": val_acc,
            "val_loss": val_loss,
            "metadata": extra_metadata or {}
        }
        torch.save(checkpoint, filepath)

    @classmethod
    def load_from_checkpoint(
        cls,
        filepath: str,
        map_location: str = "cpu"
    ) -> tuple:
        """Instantiate model and load weights from a saved checkpoint."""
        checkpoint = torch.load(filepath, map_location=map_location, weights_only=False)
        num_classes = checkpoint.get("num_classes", len(checkpoint.get("class_names", [])))
        
        model = cls(num_classes=num_classes, pretrained=False)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        
        class_names = checkpoint.get("class_names", [])
        metadata = checkpoint.get("metadata", {})
        return model, class_names, metadata
