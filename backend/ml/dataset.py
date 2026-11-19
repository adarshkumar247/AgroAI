"""AgroAI Dataset Configuration and Train/Validation Split Utilities.

Handles dataset discovery, label extraction, deterministic splitting, and DataLoader generation.
"""

import os
from dataclasses import dataclass
from typing import Tuple, List, Optional
import torch
from torch.utils.data import DataLoader, random_split, Subset
from torchvision.datasets import ImageFolder

from backend.app.ai.preprocessing import get_train_transforms, get_eval_transforms
from backend.app.ai.labels import class_manager

@dataclass
class DatasetConfig:
    data_dir: str
    val_split: float = 0.20
    batch_size: int = 16
    seed: int = 42
    num_workers: int = 0  # 0 is safest on Windows platforms

class TransformedSubset(torch.utils.data.Dataset):
    """Wraps a Subset with a specific torchvision transform pipeline."""
    def __init__(self, subset: Subset, transform):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, idx):
        x, y = self.subset[idx]
        if self.transform:
            x = self.transform(x)
        return x, y

    def __len__(self):
        return len(self.subset)

def prepare_dataloaders(
    config: DatasetConfig,
    classes_save_path: Optional[str] = None
) -> Tuple[DataLoader, DataLoader, List[str]]:
    """Create train and validation DataLoaders from a standard ImageFolder directory."""
    if not os.path.exists(config.data_dir):
        raise FileNotFoundError(f"Dataset directory '{config.data_dir}' does not exist.")

    # Base dataset without transforms to inspect structure
    raw_dataset = ImageFolder(root=config.data_dir)
    class_names = raw_dataset.classes
    num_samples = len(raw_dataset)

    if num_samples == 0:
        raise ValueError(f"No image files found in '{config.data_dir}'.")

    # Update and save dynamic class manager
    class_manager.class_names = class_names
    if classes_save_path:
        class_manager.save_classes(classes_save_path)

    # Deterministic split
    val_size = int(num_samples * config.val_split)
    train_size = num_samples - val_size

    generator = torch.Generator().manual_seed(config.seed)
    train_subset, val_subset = random_split(raw_dataset, [train_size, val_size], generator=generator)

    # Attach training and evaluation transforms
    train_dataset = TransformedSubset(train_subset, transform=get_train_transforms())
    val_dataset = TransformedSubset(val_subset, transform=get_eval_transforms())

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=False
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=False
    )

    return train_loader, val_loader, class_names
