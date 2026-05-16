# CNN vs Vision Transformers: Pipeline Differences

## Table of Contents
1. CNN Inductive Biases
2. ViT: Lack of Inductive Bias
3. AugReg and the 10× Data Rule
4. Training Recipe Comparison

---

## CNN Inductive Biases

Two fundamental inductive biases of CNN architectures:

### 1. Locality
- Nearby pixels are highly correlated
- Correlation decreases with distance

### 2. Weight Sharing → Translation Equivariance
```
f(T_t(x)) = T_t(f(x))
```
- If an object shifts 10px right → activation in the feature map also shifts 10px right
- Max Pooling → local translation invariance

**Result:** CNNs learn effectively even with limited data. Mild augmentation is sufficient.

---

## ViT: Lack of Inductive Bias

### Self-Attention: Permutation Invariant
```
Attention(ΠX) = Π · Attention(X)
```
- The attention mechanism does not care about the spatial ordering of patches
- No assumptions about 2D topology whatsoever
- All spatial relationships must be learned entirely from data

**Result:**
- Massive data (JFT-300M) → surpasses CNNs (flexibility advantage)
- Small data (ImageNet-1K) → catastrophic overfitting, falls behind even ResNet50

---

## AugReg and the 10× Data Rule

Steiner et al. (2021) — "How to train your ViT?":

- AugReg = Augmentation + Regularization → mandatory for ViT
- Aggressive RandAugment + MixUp(0.8) + CutMix(1.0) + Label Smoothing(10%)
- **10× Data Rule:** Effective AugReg ≈ training with 10× more data without augmentation

---

## Training Recipe Comparison

| Parameter | ResNet50 | DeiT-S | Rationale |
|---|---|---|---|
| Optimizer | SGD | AdamW | ViT's irregular loss surface → adaptive momentum needed |
| RandAugment | None/Mild | M=9, N=2 | ViT requires aggressive variation |
| MixUp α | 0/≤0.2 | 0.8 | Prevents ViT global overconfidence |
| CutMix α | 0/≤0.2 | 1.0 | Pushes ViT to search for local details |
| Label Smoothing | 0% | 10% | Softens overconfident predictions |
| Stochastic Depth | None | p=0.1 | Prevents co-adaptation |
| Weight Decay | 1e-4 | 0.05 | Stronger regularization for ViT |

### References
- Steiner et al. (2021): [arXiv](https://arxiv.org/abs/2106.10270)
- Touvron et al. (2021) DeiT: [arXiv](https://arxiv.org/abs/2012.12877)
- Wightman et al. (2021): [OpenReview](https://openreview.net/pdf?id=NG6MJnVl6M5)
