"""AgroAI PyTorch Model Evaluation Pipeline.

Computes loss, Top-1 accuracy, Top-3 accuracy, and per-class classification metrics
over any validation or test DataLoader.
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from backend.ml.metrics import ClassificationMetrics

def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: Optional[nn.Module] = None,
    device: str = "cpu",
    class_names: Optional[list] = None
) -> Tuple[float, Dict[str, Any]]:
    """Evaluate model on a dataset.

    Args:
        model: AgroDiseaseClassifier PyTorch module.
        dataloader: PyTorch DataLoader for evaluation.
        criterion: Optional loss function (e.g. CrossEntropyLoss).
        device: 'cpu' or 'cuda'.
        class_names: List of class names for reporting.

    Returns:
        Tuple of (average_loss, metrics_dict)
    """
    model.eval()
    model.to(device)

    if criterion is None:
        criterion = nn.CrossEntropyLoss()

    num_classes = getattr(model, "num_classes", len(class_names) if class_names else 10)
    metrics = ClassificationMetrics(num_classes=num_classes, class_names=class_names)

    total_loss = 0.0
    total_batches = 0

    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, targets)

            total_loss += loss.item()
            total_batches += 1

            metrics.update(outputs, targets)

    avg_loss = total_loss / max(total_batches, 1)
    results = metrics.compute(top_k=min(3, num_classes))
    results["loss"] = round(avg_loss, 4)

    return avg_loss, results
