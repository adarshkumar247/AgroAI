"""AgroAI Transfer Learning Training Pipeline.

Trains MobileNetV3-Small on agricultural plant pathology datasets.
Optimized for CPU execution, robust data augmentation, and automatic checkpointing.
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

# Ensure backend package is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.ai.model import AgroDiseaseClassifier
from backend.ml.dataset import DatasetConfig, prepare_dataloaders
from backend.ml.evaluate import evaluate_model

def train(
    data_dir: str,
    epochs: int = 5,
    batch_size: int = 16,
    lr: float = 1e-3,
    val_split: float = 0.20,
    save_path: str = "backend/models/best_model.pth",
    device: str = "cpu"
) -> Dict[str, Any]:
    """Execute transfer learning on CPU or GPU.

    Workflow:
      1. Prepare datasets & DataLoaders with deterministic 80/20 train/val split.
      2. Initialize MobileNetV3-Small with custom agricultural head.
      3. Freeze backbone feature extractor (576-dim) to maximize CPU efficiency.
      4. Train with CrossEntropyLoss and AdamW optimizer.
      5. Evaluate on validation set after each epoch.
      6. Checkpoint model weights when validation accuracy improves.
    """
    print("=" * 60)
    print(" AgroAI MobileNetV3-Small Crop Disease Training Pipeline")
    print("=" * 60)
    print(f"Dataset directory : {data_dir}")
    print(f"Device            : {device}")
    print(f"Batch size        : {batch_size}")
    print(f"Initial LR        : {lr}")
    print(f"Target epochs     : {epochs}")
    print("-" * 60)

    # 1. Prepare Data
    config = DatasetConfig(
        data_dir=data_dir,
        val_split=val_split,
        batch_size=batch_size,
        seed=42,
        num_workers=0
    )

    models_dir = os.path.dirname(os.path.abspath(save_path))
    os.makedirs(models_dir, exist_ok=True)
    classes_save_path = os.path.join(models_dir, "classes.json")

    print("[1/5] Loading and splitting dataset...")
    train_loader, val_loader, class_names = prepare_dataloaders(
        config=config,
        classes_save_path=classes_save_path
    )
    num_classes = len(class_names)
    print(f"  -> Discovered {num_classes} classes: {class_names}")
    print(f"  -> Training batches: {len(train_loader)}, Validation batches: {len(val_loader)}")

    # 2. Model Setup
    print("[2/5] Initializing MobileNetV3-Small architecture...")
    model = AgroDiseaseClassifier(num_classes=num_classes, pretrained=True)
    model.to(device)

    # Freeze backbone for lightweight CPU transfer learning
    model.freeze_backbone(True)
    model.unfreeze_head()

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  -> Trainable parameters: {trainable_params:,} / {total_params:,} (Backbone frozen)")

    # 3. Criterion, Optimizer, Scheduler
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_acc = 0.0
    training_history = []

    print("[3/5] Starting training loop...")
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()

        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (images, targets) in enumerate(train_loader, 1):
            images = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

            if batch_idx % max(1, len(train_loader) // 4) == 0 or batch_idx == len(train_loader):
                batch_acc = 100.0 * correct / max(total, 1)
                avg_batch_loss = running_loss / max(total, 1)
                print(f"  Epoch {epoch}/{epochs} | Batch {batch_idx}/{len(train_loader)} | Loss: {avg_batch_loss:.4f} | Acc: {batch_acc:.1f}%")

        scheduler.step()

        train_acc = correct / max(total, 1)
        train_loss = running_loss / max(total, 1)

        # 4. Validation evaluation
        val_loss, val_metrics = evaluate_model(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
            class_names=class_names
        )
        val_acc = val_metrics["accuracy"]
        duration = time.time() - epoch_start

        print(f"Epoch [{epoch}/{epochs}] ({duration:.1f}s) - Train Loss: {train_loss:.4f}, Train Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f}, Val Acc: {val_acc*100:.2f}% (Macro F1: {val_metrics['macro_f1']:.4f})")

        record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "macro_f1": val_metrics["macro_f1"]
        }
        training_history.append(record)

        # 5. Checkpoint Saving
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            print(f"  * New best validation accuracy: {best_val_acc*100:.2f}%. Saving checkpoint to {save_path}")
            model.save_checkpoint(
                filepath=save_path,
                class_names=class_names,
                epoch=epoch,
                val_acc=val_acc,
                val_loss=val_loss,
                extra_metadata={
                    "history": training_history,
                    "num_classes": num_classes,
                    "model_architecture": "MobileNetV3-Small"
                }
            )

    # 6. Load Best Model and Generate Comprehensive Final Evaluation Report
    print("\n" + "=" * 65)
    print(" Running Full Evaluation with Best Checkpoint")
    print("=" * 65)
    best_model, loaded_classes, meta = AgroDiseaseClassifier.load_from_checkpoint(save_path, map_location=device)
    val_loss, final_metrics = evaluate_model(
        model=best_model,
        dataloader=val_loader,
        criterion=criterion,
        device=device,
        class_names=class_names
    )

    print(f"\nFinal Validation Summary:")
    print(f"  Overall Top-1 Accuracy: {final_metrics['accuracy'] * 100:.2f}%")
    print(f"  Top-3 Accuracy:         {final_metrics.get('top_3_accuracy', 0.0) * 100:.2f}%")
    print(f"  Macro-F1 Score:         {final_metrics['macro_f1']:.4f}")
    print(f"  Validation Loss:        {final_metrics['loss']:.4f}")
    print(f"  Total Validation Images: {final_metrics['total_samples']}")

    print("\nPer-Class Performance:")
    print(f"  {'Class Name':<34} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}")
    print("  " + "-" * 80)
    for cname, stats in final_metrics["per_class"].items():
        print(f"  {cname:<34} | {stats['precision']:<10.4f} | {stats['recall']:<10.4f} | {stats['f1_score']:<10.4f} | {stats['support']:<8}")

    print("\nConfusion Matrix (Rows = Ground Truth, Columns = Predicted):")
    header = "       " + " ".join([f"[{i:02d}]" for i in range(num_classes)])
    print(header)
    for idx, row in enumerate(final_metrics["confusion_matrix"]):
        row_str = " ".join([f"{val:4d}" for val in row])
        print(f"  [{idx:02d}] {row_str}")

    metrics_save_path = os.path.join(models_dir, "metrics_report.json")
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2)
    print(f"\nSaved full metrics and confusion matrix to: {metrics_save_path}")

    total_duration = time.time() - start_time
    print("=" * 65)
    print(f" Training complete in {total_duration:.1f}s. Best Val Accuracy: {best_val_acc*100:.2f}%")
    print(f" Saved checkpoint: {save_path}")
    print(f" Saved class list: {classes_save_path}")
    print("=" * 65)

    return {
        "best_val_acc": best_val_acc,
        "classes": class_names,
        "save_path": save_path,
        "metrics": final_metrics,
        "history": training_history
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroAI Plant Disease Training on MobileNetV3-Small")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to dataset root folder")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--val-split", type=float, default=0.20, help="Validation set split ratio")
    parser.add_argument("--save-path", type=str, default="backend/models/best_model.pth", help="Checkpoint save path")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")

    args = parser.parse_args()
    train(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        val_split=args.val_split,
        save_path=args.save_path,
        device=args.device
    )
