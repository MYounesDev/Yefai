---
name: ml-reproducibility-seed-control
description: >
  Comprehensive seed management, cuDNN/cuBLAS configuration, and PRNG control
  for achieving full reproducibility and determinism in single-node NVIDIA GPU
  machine learning and deep learning workflows.
  Use when: (1) PyTorch or scikit-learn models produce different results across
  runs, (2) a set_reproducibility function needs to be written or updated,
  (3) the difference between TRNG and PRNG or the seed mechanism needs to be
  explained, (4) cuDNN benchmark/deterministic flags or CUBLAS_WORKSPACE_CONFIG
  need to be configured, (5) random_state usage in scikit-learn is in question.
---

# ML Reproducibility & Seed Control

Comprehensive guide for making machine learning workflows deterministic on
single-node NVIDIA GPU environments.

## Core Concepts

- **TRNG**: Generated from hardware entropy (thermal noise, RDRAND). Cannot be replayed.
- **PRNG**: Deterministic mathematical algorithm (Mersenne Twister, Philox). Can be locked with a seed.
- **Seed**: Fixes the PRNG's initial state (S₀) → same seed = same number sequence.

Sources of non-determinism (setting a seed alone is not enough):
1. **IEEE 754 floating-point non-associativity** — rounding errors accumulate when addition order changes
2. **cuDNN benchmark mode** — may select a different algorithm on each run
3. **atomicAdd races** — GPU threads write to memory in a different order each run
4. **cuBLAS workspace** — dynamic memory allocation creates races across multiple streams
5. **PYTHONHASHSEED** — dict/set iteration order can be random

## Ready-to-Use Function

```python
import os, random, warnings
import numpy as np
import torch

def set_reproducibility(seed_value: int = 42) -> None:
    """
    Ensures full reproducibility on a single-node NVIDIA GPU environment.
    Call BEFORE model definition, DataLoader, and optimizer instantiation.
    """
    # 1. OS / Environment variables
    os.environ["PYTHONHASHSEED"] = str(seed_value)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"  # requires CUDA 10.2+

    # 2. Python & NumPy PRNG
    random.seed(seed_value)
    np.random.seed(seed_value)

    # 3. PyTorch CPU & GPU
    torch.manual_seed(seed_value)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)

    # 4. cuDNN hardware constraints
    torch.backends.cudnn.benchmark     = False  # disable dynamic algorithm selection
    torch.backends.cudnn.deterministic = True   # use only deterministic kernels

    # 5. PyTorch strict determinism mode
    try:
        torch.use_deterministic_algorithms(True)
    except AttributeError:
        warnings.warn("PyTorch < 1.8: falling back to set_deterministic.")
        torch.set_deterministic(True)
    except RuntimeError as e:
        warnings.warn(f"Deterministic mode error: {e}. "
                      "Make sure CUBLAS_WORKSPACE_CONFIG is set before imports.")
```

> **Warning:** `torch.use_deterministic_algorithms(True)` may fall back certain
> CUDA kernels to CPU or raise a `RuntimeError`. Some performance overhead is expected.

## scikit-learn Special Rule

Global `np.random.seed()` is unreliable with parallel `joblib` workers.
Pass **local** `random_state` to every object:

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

SEED = 42
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED   # ← local seeding
)
clf = RandomForestClassifier(n_estimators=100, random_state=SEED)
```

## Configuration Checklist

| Layer | Parameter | Value |
|-------|-----------|-------|
| OS | `PYTHONHASHSEED` | `str(seed)` |
| OS | `CUBLAS_WORKSPACE_CONFIG` | `":16:8"` or `":4096:2"` |
| Python | `random.seed()` | `seed` |
| NumPy | `np.random.seed()` | `seed` |
| PyTorch CPU | `torch.manual_seed()` | `seed` |
| PyTorch GPU | `torch.cuda.manual_seed_all()` | `seed` |
| cuDNN | `cudnn.benchmark` | `False` |
| cuDNN | `cudnn.deterministic` | `True` |
| PyTorch | `use_deterministic_algorithms(True)` | — |

For detailed mechanism explanations → `references/determinism-deep-dive.md`

## Common Issues

- **RuntimeError: nondeterministic operation**: A kernel with no deterministic counterpart was triggered while `torch.use_deterministic_algorithms(True)` is active. Move the operation to CPU or use `warn_only=True`.
- **Results still differ across runs**: `CUBLAS_WORKSPACE_CONFIG` must be set before Python imports; set it from the shell or via `subprocess.Popen(env=...)` rather than inside the script with `os.environ`.
- **scikit-learn parallel CV inconsistent**: There is no `GridSearchCV(random_state=...)` — pass `random_state` to each individual estimator.
