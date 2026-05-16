# Snakefile — Yefai Phase 2A: Anomalib Training & Embedding Pipeline
#
# Usage:
#   cd server && uv run snakemake -c1 all       # run full pipeline (extract → stats → train → export)
#   cd server && uv run snakemake -c1 train      # run up to training
#   cd server && uv run snakemake -c1 --dry-run  # dry run
#
# Data leakage önlemleri:
#   - Mean/std sadece train normal (wear<=45) görüntülerden hesaplanır
#   - Split set-bazlıdır (1-12 train, 13-17 test) — aynı set asla iki split'te olmaz
#   - Train setine anomaly/wear>45 görüntü girmez
#   - Test setinden tek bir piksel bile mean/std hesabına girmez

PROJECT_ROOT = ".."
DATA_DIR = f"{PROJECT_ROOT}/data"
MODELS_DIR = f"{PROJECT_ROOT}/models"
SERVER_DIR = "."

STATS_FILE = f"{DATA_DIR}/normalization_stats.json"
LABELS_CSV = f"{SERVER_DIR}/dataset/labels.csv"
MATWI_DIR = f"{DATA_DIR}/MATWI"
DATASET_DIR = f"{DATA_DIR}/anomalib_format"
CHECKPOINT = f"{MODELS_DIR}/checkpoint.ckpt"
MODEL_PT = f"{MODELS_DIR}/patchcore_matwi.pt"
MODEL_META = f"{MODELS_DIR}/model_meta.json"

rule all:
    input:
        MODEL_PT,
        MODEL_META,


rule unzip_data:
    """Extract MATWI Set*.zip files to data/MATWI/.
    Skips if already extracted."""
    input:
        zip_files=expand(
            f"{SERVER_DIR}/dataset/Set{{n}}.zip",
            n=range(1, 18),
        ),
    output:
        touch(f"{MATWI_DIR}/.extracted"),
    shell:
        "uv run python etl/unzip_data.py && touch {output}"


rule compute_stats:
    """Compute per-channel mean/std from TRAIN NORMAL images only.
    No test set pixel is used — zero data leakage.
    Output: data/normalization_stats.json with mean, std, n_images."""
    input:
        labels=LABELS_CSV,
        extracted=f"{MATWI_DIR}/.extracted",
    output:
        stats=STATS_FILE,
    shell:
        "uv run python ai/anomalib/compute_stats.py"


rule prepare_dataset:
    """Convert MATWI labels.csv to Anomalib Folder format.
    train/good/ = normal images (wear<=45) from sets 1-12
    test/good/  = normal images (wear<=45) from sets 13-17
    test/bad/   = anomaly images (wear>=90) from sets 13-17
    Mild wear (45<wear<90) excluded from both."""
    input:
        labels=LABELS_CSV,
        extracted=f"{MATWI_DIR}/.extracted",
    output:
        directory(DATASET_DIR),
    shell:
        "uv run python ai/anomalib/dataset.py"


rule train:
    """Train PatchCore (wide_resnet50_2) on normal tool wear images.
    Uses dataset-specific mean/std if normalization_stats.json exists.
    Seed 42. CUDNN deterministic mode for reproducibility.
    Output: checkpoint.ckpt + model_meta.json with normalization params."""
    input:
        dataset=DATASET_DIR,
        stats=STATS_FILE,
    output:
        checkpoint=CHECKPOINT,
        meta=MODEL_META,
    resources:
        gpu=1,
    shell:
        "uv run python ai/anomalib/train.py"


rule export:
    """Export Lightning checkpoint → patchcore_matwi.pt.
    Strips 'model.' prefix from Lightning state_dict keys.
    Validates loaded parameter count (must be >10 to prevent empty export)."""
    input:
        checkpoint=CHECKPOINT,
    output:
        model=MODEL_PT,
    shell:
        "uv run python ai/anomalib/export.py"


rule inference:
    """Run inference on test set.
    Uses normalization from model_meta.json (dataset-specific or ImageNet).
    Computes data-driven anomaly threshold from normal test images."""
    input:
        model=MODEL_PT,
    output:
        results=f"{DATA_DIR}/anomalib_inference_results.csv",
    shell:
        "uv run python ai/anomalib/inference.py"
