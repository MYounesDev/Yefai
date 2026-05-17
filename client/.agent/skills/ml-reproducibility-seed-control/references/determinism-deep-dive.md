# Determinism Deep Dive

## 1. IEEE 754 Floating-Point Non-Associativity

Under the IEEE 754 standard, addition is **not associative**:

```
(a + b) + c ≠ a + (b + c)   # for floating-point numbers
```

When thousands of GPU threads write to the same tensor element via `atomicAdd`,
the execution order changes on every run → different rounding errors → different
gradients. After hundreds of epochs, these nanometric differences compound into
visible divergence on the loss curve.

## 2. cuDNN Benchmark Mode

When `torch.backends.cudnn.benchmark = True` (or left at default):

- cuDNN profiles all available convolution algorithms (GEMM, Winograd, FFT) briefly based on tensor dimensions
- The fastest algorithm is selected as the "winner"
- A change in GPU temperature or load can cause a different algorithm to be selected on the next run
- Different algorithms → different memory access patterns → different floating-point ordering

**Fix:** `benchmark = False` + `deterministic = True`

## 3. cuBLAS Workspace Race

PyTorch uses cuBLAS for matrix multiplications. Multiple CUDA streams compete
for dynamically allocated workspace memory, creating race conditions.

`CUBLAS_WORKSPACE_CONFIG` values:
- `":16:8"` → 16 KB × 8 buffers (low memory footprint)
- `":4096:2"` → 4 MB × 2 buffers (for large tensors)

**Critical:** This variable must be set in the shell environment **before** Python
imports. Setting it inside the script with `os.environ[...] = ...` may not be
sufficient because some CUDA libraries read the environment at process startup.

Safe usage:
```bash
CUBLAS_WORKSPACE_CONFIG=:16:8 python train.py
```

Or via `.env` / `subprocess`:
```python
import subprocess
env = {**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":16:8"}
subprocess.run(["python", "train.py"], env=env)
```

## 4. PYTHONHASHSEED

In Python 3.3+, the hash table ordering of `dict` and `set` is randomized for
security reasons. If model parameters or hyperparameter dicts are iterated over,
the iteration order can vary between runs.

```bash
PYTHONHASHSEED=42 python train.py
```

## 5. PyTorch DataLoader with num_workers > 0

When using multiple workers, each worker initializes its own PRNG state.
A `worker_init_fn` must be defined:

```python
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)

g = torch.Generator()
g.manual_seed(42)

loader = DataLoader(
    dataset,
    num_workers=4,
    worker_init_fn=seed_worker,
    generator=g,
)
```

## 6. Non-Deterministic PyTorch Operations

Operations that raise an error when `torch.use_deterministic_algorithms(True)` is active:

| Operation | Alternative |
|-----------|-------------|
| `scatter_add_` (CUDA) | Move to CPU |
| `torch.bmm` (sparse) | Use dense tensor |
| `Conv3d` backward | CPU or `warn_only=True` |
| `index_add_` | Move to CPU |
| `kthvalue` | Replace with `torch.sort` |

Use `warn_only=True` to get a warning instead of an error (useful during research):
```python
torch.use_deterministic_algorithms(True, warn_only=True)
```

## 7. Seed Management in Production

Seeds are fixed during development. Before moving to production:

- Test scikit-learn models with `random_state=None` (is there overfitting to a specific seed?)
- Run with multiple seeds and measure variance in results
- Log the seed value as an artifact with MLflow / W&B:

```python
import mlflow
mlflow.log_param("seed", SEED)
```

## 8. PRNG Algorithm Comparison

| Algorithm | Used In | Period | Multi-threading |
|-----------|---------|--------|-----------------|
| Mersenne Twister (MT19937) | Python, NumPy | 2^19937-1 | Weak |
| Philox | PyTorch CUDA | 2^128 | Strong |
| PCG | Modern libraries | 2^128 | Strong |
| LCG | Legacy systems | Short | Weak |

PyTorch uses Philox on the GPU side and MT19937 on the CPU side.
