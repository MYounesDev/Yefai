import json
import logging
from pathlib import Path

import torch

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def train_patchcore(
    dataset_path: Path,
    output_dir: Path,
    device: str = "auto",
    seed: int = 42,
):
    import numpy as np
    from anomalib.data import Folder
    from anomalib.engine import Engine
    from anomalib.models import Patchcore

    torch.manual_seed(seed)
    np.random.seed(seed)

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
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
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

    if not dataset_path.exists():
        logger.error("Anomalib dataset not found at %s. Run dataset.py first.", dataset_path)
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    train_patchcore(dataset_path, output_dir)


if __name__ == "__main__":
    main()
