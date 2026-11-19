"""AgroAI Evaluation Metrics for Crop Disease Classification.

Computes Top-1 Accuracy, Top-K Accuracy, Precision, Recall, and Macro F1 Score.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import torch

class ClassificationMetrics:
    """Accumulates batch predictions and computes full-dataset classification metrics."""

    def __init__(self, num_classes: int, class_names: Optional[List[str]] = None):
        self.num_classes = num_classes
        self.class_names = class_names or [f"Class_{i}" for i in range(num_classes)]
        self.reset()

    def reset(self):
        self.all_preds = []
        self.all_targets = []
        self.all_probs = []

    def update(self, logits: torch.Tensor, targets: torch.Tensor):
        """Update metrics with a new batch of logits and targets."""
        with torch.no_grad():
            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)

            self.all_preds.extend(preds.cpu().numpy().tolist())
            self.all_targets.extend(targets.cpu().numpy().tolist())
            self.all_probs.extend(probs.cpu().numpy().tolist())

    def compute(self, top_k: int = 3) -> Dict[str, Any]:
        """Compute aggregate and per-class metrics."""
        preds = np.array(self.all_preds)
        targets = np.array(self.all_targets)
        probs = np.array(self.all_probs)

        total_samples = len(targets)
        if total_samples == 0:
            return {"accuracy": 0.0, "macro_f1": 0.0, "total_samples": 0}

        # Overall Top-1 Accuracy
        accuracy = float(np.mean(preds == targets))

        # Top-K Accuracy
        top_k_val = min(top_k, self.num_classes)
        top_k_preds = np.argsort(probs, axis=1)[:, -top_k_val:]
        top_k_acc = float(np.mean([t in top_k_preds[i] for i, t in enumerate(targets)]))

        # Confusion Matrix
        conf_matrix = np.zeros((self.num_classes, self.num_classes), dtype=int)
        for p, t in zip(preds, targets):
            conf_matrix[t, p] += 1

        # Per-Class Precision, Recall, F1
        per_class = {}
        f1_scores = []
        for i, name in enumerate(self.class_names):
            tp = conf_matrix[i, i]
            fp = np.sum(conf_matrix[:, i]) - tp
            fn = np.sum(conf_matrix[i, :]) - tp

            precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            f1_scores.append(f1)

            per_class[name] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "support": int(np.sum(conf_matrix[i, :]))
            }

        macro_f1 = float(np.mean(f1_scores))

        return {
            "accuracy": round(accuracy, 4),
            f"top_{top_k_val}_accuracy": round(top_k_acc, 4),
            "macro_f1": round(macro_f1, 4),
            "total_samples": total_samples,
            "per_class": per_class,
            "confusion_matrix": conf_matrix.tolist()
        }
