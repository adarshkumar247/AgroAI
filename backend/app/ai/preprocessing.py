"""AgroAI Image Preprocessing and Data Augmentation Pipeline.

Standardized for MobileNetV3-Small (224x224 input resolution, RGB, ImageNet normalization).
"""

import io
from typing import Union
from PIL import Image
import torch
from torchvision import transforms

# Standard ImageNet normalization coefficients
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
TARGET_SIZE = 224

def get_train_transforms():
    """Augmentation pipeline for training robustness against field lighting and angles."""
    return transforms.Compose([
        transforms.RandomResizedCrop(TARGET_SIZE, scale=(0.75, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

def get_eval_transforms():
    """Deterministic validation and inference transform pipeline."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(TARGET_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

def load_and_preprocess_image(
    image_input: Union[str, bytes, io.BytesIO, Image.Image]
) -> torch.Tensor:
    """Load an image from path or bytes and return a batched tensor of shape (1, 3, 224, 224)."""
    if isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, io.BytesIO):
        img = Image.open(image_input)
    elif isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Ensure 3-channel RGB representation (strip alpha or grayscale channels)
    if img.mode != "RGB":
        img = img.convert("RGB")

    eval_transform = get_eval_transforms()
    tensor = eval_transform(img)
    return tensor.unsqueeze(0)  # Shape: (1, 3, 224, 224)
