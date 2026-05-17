---
name: dl-image-preprocessing
description: >-
  Design mathematically and architecturally grounded data preprocessing and
  augmentation pipelines for image-based deep learning projects. Use cases:
  (1) Choosing resizing, normalization, and interpolation methods,
  (2) Understanding Z-Score normalization effects on Hessian and gradient
  stability, (3) Selecting geometric, color-space, and Mixed-Sample
  (Cutout/MixUp/CutMix) augmentation techniques, (4) Differentiating pipeline
  recipes for CNN vs Vision Transformer architectures, (5) Optimizing
  PyTorch/Albumentations pipelines for throughput. Triggers: image preprocessing,
  data augmentation, augmentation pipeline, ViT training recipe, CNN training
  recipe, MixUp, CutMix, RandAugment, albumentations, normalization,
  interpolation, resizing, label smoothing, label invariance breakage.
---

# DL Image Preprocessing & Augmentation Guide

In image-based deep learning, the data preprocessing and augmentation pipeline
is a critical design decision that directly determines the loss landscape
topology, gradient dynamics, and the model's generalization capacity — it is
not a mere format conversion step.

## Quick Decision Flow

1. **Identify architecture type** → CNN or ViT?
2. **Choose interpolation method** → General: Bilinear; Medical/fine-detail: Bicubic
3. **Configure normalization** → Transfer learning: ImageNet μ/σ; From scratch: own μ/σ
4. **Set augmentation intensity** → CNN: mild; ViT: aggressive (AugReg mandatory)
5. **Select MSDA strategy** → Occlusion: CutMix; Global noise: MixUp
6. **Optimize pipeline performance** → cv2 thread lock, crop-first, late float cast

## 1. Preprocessing

### 1.1 Interpolation Method Selection

| Method | Pixels | Continuity | When to Use |
|---|---|---|---|
| Nearest Neighbor | 1 | Discontinuous | Rarely in DL — only for segmentation masks |
| **Bilinear** | 4 (2×2) | Function continuous | **Standard for CNN/ViT training** |
| Bicubic | 16 (4×4) | Function + 1st derivative continuous | Medical/radiological/high-detail tasks |

- Bilinear acts as a natural low-pass filter, reducing aliasing
- Bicubic preserves edges and textures better but costs ~4× more FLOPs
- `torchvision.transforms.Resize(size, interpolation=InterpolationMode.BILINEAR)`

### 1.2 Z-Score Normalization

Formula: `x_normalized = (x - μ) / σ` (per channel)

**ImageNet statistics** (mandatory for transfer learning):
```
mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]
```

**Alternative schemes:**
- Inception: `μ=0.5, σ=0.5` → [-1, 1] range
- YOLO: no mean subtraction, only /255

**Why is this critical?** Detailed theory → [references/01-normalization-theory.md](references/01-normalization-theory.md)

Short summary:
- Unnormalized data → isolated large eigenvalues in the Hessian → κ(H) ≫ 1 (ill-conditioned)
- Loss surface forms narrow, steep valleys → gradient zig-zags
- Z-Score → isotropic input → spherical loss surface → stable convergence
- Also mitigates vanishing/exploding gradient risk

## 2. Data Augmentation

### 2.1 Basic Layers

**Geometric transforms:** RandomResizedCrop, Flip, Rotation, Affine
- Strengthens translation equivariance
- RandomResizedCrop: breaks center-framing bias

**Color manipulations:** ColorJitter (brightness, contrast, saturation, hue)
- Breaks spurious color/texture correlations
- Forces the model to learn shape/contour features

### 2.2 Mixed-Sample Data Augmentation (MSDA)

Detailed mathematical analysis → [references/02-augmentation-techniques.md](references/02-augmentation-techniques.md)

| Technique | Mechanism | Best Scenario |
|---|---|---|
| **Cutout** | Random rectangular masking | Prevents over-reliance on a single feature |
| **MixUp** | Pixel-wise weighted combination of two samples | Global noise/blur robustness |
| **CutMix** | Cut a rectangle from one image, paste onto another | Occlusion robustness, local feature learning |

**Selection rule:**
- **MixUp** → distance-independent, global regularization; Gaussian noise/blur
- **CutMix** → distance-sensitive, local regularization; occlusion, partial objects

### 2.3 Augmentation Risk Scenarios

**Label invariance breakage:**
- OCR/MNIST: "6" → 180° rotation → "9" (label remains "6")
- Medical: asymmetry/orientation carries diagnostic information

**Domain structure corruption:**
- Wildlife monitoring: habitat background is a robust feature
- Aggressive cutout/color equalization destroys this signal → OOD accuracy drops 3–15%

**Runtime overhead:**
- Heavy augmentations create CPU bottlenecks → GPU idles → training slows 20–30%

## 3. CNN vs ViT Pipeline Differences

Detailed comparison table → [references/03-cnn-vs-vit.md](references/03-cnn-vs-vit.md)

### CNN (ResNet etc.)
- **Built-in inductive bias:** locality + weight sharing → translation equivariance
- Effective learning even with limited data
- Mild augmentation is sufficient

### ViT (DeiT etc.)
- **No inductive bias:** permutation-invariant self-attention
- Must learn all spatial relationships from data
- **AugReg mandatory:** catastrophic overfitting without aggressive augmentation
- "10× Data" rule: Effective AugReg ≈ 10× data effect

### Quick Recipe Comparison

| Parameter | CNN (ResNet) | ViT (DeiT) |
|---|---|---|
| Optimizer | SGD | AdamW |
| RandAugment | None/Mild | Strong (M=9, N=2) |
| MixUp α | 0 / ≤0.2 | 0.8 |
| CutMix α | 0 / ≤0.2 | 1.0 |
| Label Smoothing | 0% | 10% |
| Stochastic Depth | None | p=0.1 |

## 4. Pipeline Optimization Principles

1. **`cv2.setNumThreads(0)`** → Prevent DataLoader worker / OpenCV thread conflicts
2. **Crop first** → Run heavy transforms on smaller crops, not full-resolution images
3. **Late float cast** → Stay in uint8, convert to float32 only after Normalize
4. **Batch-level MSDA** → Apply MixUp/CutMix on GPU via `torchvision.transforms.v2`

Full working pipeline code → [templates/vit_pipeline.py](templates/vit_pipeline.py)

## 5. Reference Files

| File | Contents |
|---|---|
| [references/01-normalization-theory.md](references/01-normalization-theory.md) | Hessian, condition number, vanishing/exploding gradient theory |
| [references/02-augmentation-techniques.md](references/02-augmentation-techniques.md) | MixUp/CutMix/Cutout math and Park et al. (2022) analysis |
| [references/03-cnn-vs-vit.md](references/03-cnn-vs-vit.md) | Architectural inductive bias, AugReg, DeiT recipe details |
| [templates/vit_pipeline.py](templates/vit_pipeline.py) | Production-ready PyTorch+Albumentations ViT pipeline |
