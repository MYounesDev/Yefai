"""
Production-Ready ViT/DeiT Training Pipeline
=============================================
Optimized image preprocessing and augmentation with PyTorch + Albumentations.

Optimization principles:
1. cv2.setNumThreads(0) → Prevent DataLoader/OpenCV thread conflicts
2. Crop first → Reduce CPU load by running heavy transforms on smaller crops
3. Late float cast → Stay in uint8 to save RAM until after Normalize
4. Batch-level MSDA → Apply MixUp/CutMix on GPU

Usage:
    Copy this template into your project and update image_paths, labels,
    and num_classes to match your dataset.
"""

import os
import cv2
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torchvision.transforms import v2

# ==========================================================================
# 1. OPTIMIZATION: Prevent OpenCV thread conflicts
# ==========================================================================
cv2.setNumThreads(0)
cv2.ocl.setUseOpenCL(False)


class OptimizedViTDataset(Dataset):
    """
    Optimized dataset for ViT/DeiT training.

    Key principles:
    - Albumentations augmentations in uint8 space (CPU-friendly)
    - Crop first: RandomResizedCrop comes first in the pipeline
    - Float32 conversion only after Normalize
    - ImageNet statistics (transfer learning compatible)
    """

    def __init__(
        self,
        image_paths: list[str],
        labels: list[int],
        is_train: bool = True,
        img_size: int = 224,
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.is_train = is_train

        if self.is_train:
            self.transform = A.Compose([
                # --- Crop First: reduce CPU load ---
                A.RandomResizedCrop(
                    height=img_size, width=img_size,
                    scale=(0.08, 1.0),
                    ratio=(3/4, 4/3),
                    interpolation=cv2.INTER_LINEAR,  # Bilinear
                ),
                A.HorizontalFlip(p=0.5),

                # --- RandAugment-style (DeiT recipe: N=2, M=9) ---
                A.OneOf([
                    A.ColorJitter(
                        brightness=0.4, contrast=0.4,
                        saturation=0.4, hue=0.1, p=1.0,
                    ),
                    A.RandomBrightnessContrast(
                        brightness_limit=0.3,
                        contrast_limit=0.3, p=1.0,
                    ),
                    A.HueSaturationValue(
                        hue_shift_limit=20,
                        sat_shift_limit=30,
                        val_shift_limit=20, p=1.0,
                    ),
                ], p=0.9),

                A.OneOf([
                    A.ShiftScaleRotate(
                        shift_limit=0.1, scale_limit=0.15,
                        rotate_limit=30, p=1.0,
                    ),
                    A.Affine(
                        shear=(-15, 15), p=1.0,
                    ),
                ], p=0.5),

                # --- Cutout (Random Erasing) ---
                A.CoarseDropout(
                    max_holes=1,
                    max_height=int(img_size * 0.25),
                    max_width=int(img_size * 0.25),
                    fill_value=0, p=0.25,
                ),

                # --- Z-Score Normalization (ImageNet μ/σ) ---
                # uint8 [0,255] → float32 [normalized]
                A.Normalize(
                    mean=(0.485, 0.456, 0.406),
                    std=(0.229, 0.224, 0.225),
                    max_pixel_value=255.0,
                ),

                # --- HWC → CHW tensor conversion ---
                ToTensorV2(),
            ])
        else:
            self.transform = A.Compose([
                A.Resize(
                    height=int(img_size * 256 / 224),
                    width=int(img_size * 256 / 224),
                    interpolation=cv2.INTER_LINEAR,
                ),
                A.CenterCrop(height=img_size, width=img_size),
                A.Normalize(
                    mean=(0.485, 0.456, 0.406),
                    std=(0.229, 0.224, 0.225),
                    max_pixel_value=255.0,
                ),
                ToTensorV2(),
            ])

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        # Read with OpenCV (generally faster than PIL)
        image = cv2.imread(self.image_paths[idx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # uint8

        label = torch.tensor(self.labels[idx], dtype=torch.int64)

        augmented = self.transform(image=image)
        image = augmented["image"]  # (3, H, W) float32

        return image, label


# ==========================================================================
# TRAINING LOOP — Batch-Level MSDA (MixUp + CutMix)
# ==========================================================================

def create_dataloader(
    image_paths: list[str],
    labels: list[int],
    batch_size: int = 128,
    is_train: bool = True,
    num_workers: int = 8,
    img_size: int = 224,
) -> DataLoader:
    """Create an optimized DataLoader."""
    dataset = OptimizedViTDataset(
        image_paths=image_paths,
        labels=labels,
        is_train=is_train,
        img_size=img_size,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_train,
        num_workers=num_workers,
        pin_memory=True,     # Speeds up GPU transfer
        drop_last=is_train,  # Fixed batch size for batch-level MSDA
    )


def create_msda_transform(num_classes: int):
    """
    Create batch-level MixUp + CutMix transform for GPU.

    Using torchvision.transforms.v2:
    - Randomly selects MixUp or CutMix at each iteration
    - Labels are automatically converted to one-hot soft labels
    """
    mixup = v2.MixUp(alpha=0.8, num_classes=num_classes)
    cutmix = v2.CutMix(alpha=1.0, num_classes=num_classes)
    return v2.RandomChoice([mixup, cutmix])


def train_one_epoch(
    model,
    train_loader: DataLoader,
    optimizer,
    loss_fn,
    msda_transform,
    device: str = "cuda",
):
    """
    Single epoch training loop.

    IMPORTANT: When MSDA is applied, labels are converted to (B, num_classes)
    soft label format. CrossEntropyLoss must support soft targets.
    label_smoothing=0.1 is recommended for ViT.
    """
    model.train()
    total_loss = 0.0

    for images, labels in train_loader:
        # Asynchronous GPU transfer
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        # Batch-level MSDA on GPU
        images, labels = msda_transform(images, labels)

        # Forward pass
        outputs = model(images)
        loss = loss_fn(outputs, labels)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(train_loader)


# ==========================================================================
# USAGE EXAMPLE
# ==========================================================================

if __name__ == "__main__":
    # Example configuration
    NUM_CLASSES = 1000
    BATCH_SIZE = 128
    EPOCHS = 300
    LR = 1e-3
    WEIGHT_DECAY = 0.05
    LABEL_SMOOTHING = 0.1

    # Add your data paths and labels here
    train_paths = ["/path/to/img1.jpg"]  # TODO: real paths
    train_labels = [0]                    # TODO: real labels

    # DataLoader
    train_loader = create_dataloader(
        train_paths, train_labels,
        batch_size=BATCH_SIZE,
    )

    # MSDA transform
    msda = create_msda_transform(NUM_CLASSES)

    # Model (example: using timm library)
    # import timm
    # model = timm.create_model("deit_small_patch16_224", pretrained=True,
    #                           num_classes=NUM_CLASSES).cuda()

    # Optimizer (AdamW — standard for ViT)
    # optimizer = torch.optim.AdamW(
    #     model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY
    # )

    # Loss (with Label Smoothing support)
    loss_fn = torch.nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)

    # Training loop
    # for epoch in range(EPOCHS):
    #     avg_loss = train_one_epoch(
    #         model, train_loader, optimizer, loss_fn, msda
    #     )
    #     print(f"Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.4f}")
