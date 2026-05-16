import json
import logging
from pathlib import Path

import torch

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_norm_stats(stats_path: Path | None) -> tuple[list[float], list[float]]:
    if stats_path is not None and stats_path.exists():
        stats = json.loads(stats_path.read_text())
        mean = stats["mean"]
        std = stats["std"]
        logger.info("Using dataset-specific normalization from %s", stats_path)
        logger.info(
            "  MATWI mean=%s, std=%s (n=%d train normal images)", mean, std, stats["n_images"]
        )
        return mean, std
    else:
        logger.info("Using ImageNet normalization (no stats file at %s)", stats_path)
        return IMAGENET_MEAN, IMAGENET_STD


def train_patchcore(
    dataset_path: Path,
    output_dir: Path,
    norm_stats_path: Path | None = None,
    device: str = "auto",
    seed: int = 42,
):
    import numpy as np
    from anomalib.data import Folder
    from anomalib.engine import Engine
    from anomalib.models import Patchcore

    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    mean, std = load_norm_stats(norm_stats_path)

    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    logger.info("Training on device: %s (seed=%d)", device, seed)

    datamodule = Folder(
        name="matwi",
        root=str(dataset_path),
        normal_dir="train/good",
        abnormal_dir="test/bad",
        normal_test_dir="test/good",
        image_size=(256, 256),
        train_batch_size=32,
        eval_batch_size=32,
        num_workers=4,
    )

    if norm_stats_path is not None and norm_stats_path.exists():
        from torchvision.transforms import Compose, Normalize, Resize, ToTensor

        custom_transform = Compose(
            [
                Resize((256, 256), antialias=True),
                ToTensor(),
                Normalize(mean=mean, std=std),
            ]
        )
        datamodule.train_transform = custom_transform
        datamodule.eval_transform = custom_transform
        logger.info("Applied dataset-specific transform with MATWI normalization")

    datamodule.setup()

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=("layer2", "layer3"),
        pre_trained=True,
        coreset_sampling_ratio=0.1,
        num_neighbors=9,
    )

    engine = Engine(
        max_epochs=1,
        devices=1,
        accelerator="auto" if device == "mps" else device,
        default_root_dir=str(output_dir / "logs"),
    )

    logger.info("Starting PatchCore training (feature extraction + memory bank)...")
    engine.fit(model=model, datamodule=datamodule)

    checkpoint_path = output_dir / "checkpoint.ckpt"
    engine.trainer.save_checkpoint(str(checkpoint_path))
    logger.info("Checkpoint saved: %s", checkpoint_path)

    memory_bank = getattr(model.model, "memory_bank", None)
    if memory_bank is not None:
        mem_shape = memory_bank.shape if hasattr(memory_bank, "shape") else "N/A"
        logger.info("Memory bank shape: %s", mem_shape)

    model_meta = {
        "backbone": "wide_resnet50_2",
        "layers": ["layer2", "layer3"],
        "image_size": [256, 256],
        "coreset_sampling_ratio": 0.1,
        "num_neighbors": 9,
        "device": device,
        "seed": seed,
        "normalization": {
            "mean": mean,
            "std": std,
            "source": "MATWI train normal" if norm_stats_path else "ImageNet",
        },
    }
    meta_path = output_dir / "model_meta.json"
    meta_path.write_text(json.dumps(model_meta, indent=2))
    logger.info("Model metadata saved: %s", meta_path)

    return model, str(checkpoint_path)


def main():
    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent.parent
    project_root = server_root.parent

    dataset_path = project_root / "data" / "anomalib_format"
    output_dir = project_root / "models"
    norm_stats_path = project_root / "data" / "normalization_stats.json"

    if not dataset_path.exists():
        logger.error("Anomalib dataset not found at %s. Run dataset.py first.", dataset_path)
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    train_patchcore(dataset_path, output_dir, norm_stats_path=norm_stats_path)


if __name__ == "__main__":
    main()
