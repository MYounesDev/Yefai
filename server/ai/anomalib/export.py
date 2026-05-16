import json
import logging
from pathlib import Path

import torch

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def export_model(checkpoint_path: Path, output_dir: Path) -> Path:
    from anomalib.models import Patchcore

    checkpoint = torch.load(str(checkpoint_path), map_location="cpu", weights_only=False)

    raw_state_dict = checkpoint.get("state_dict", checkpoint)
    state_dict = {}
    for key, value in raw_state_dict.items():
        clean_key = key.removeprefix("model.").removeprefix("teacher.")
        state_dict[clean_key] = value

    logger.info(
        "State dict keys: %d raw, %d cleaned (model. prefix stripped)",
        len(raw_state_dict),
        len(state_dict),
    )

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=("layer2", "layer3"),
        pre_trained=False,
        coreset_sampling_ratio=0.1,
        num_neighbors=9,
    )
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    if missing:
        logger.warning("Missing keys (%d): %s...", len(missing), str(missing[:3]))
    if unexpected:
        logger.warning("Unexpected keys (%d): %s...", len(unexpected), str(unexpected[:3]))

    loaded_param_count = sum(1 for k in state_dict if k in model.state_dict())
    logger.info(
        "Loaded %d/%d parameters from checkpoint",
        loaded_param_count,
        len(model.state_dict()),
    )

    if loaded_param_count < 10:
        raise RuntimeError(
            f"Only {loaded_param_count} parameters loaded — checkpoint may be corrupt "
            "or state_dict key mismatch. Expected ~800+ parameters."
        )

    model.eval()

    pt_path = output_dir / "patchcore_matwi.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "backbone": "wide_resnet50_2",
            "layers": ["layer2", "layer3"],
        },
        str(pt_path),
    )
    logger.info("Model exported to %s (%.2f MB)", pt_path, pt_path.stat().st_size / 1e6)

    verify_path = output_dir / "patchcore_matwi_verify.json"
    verify_data = {
        "pt_path": str(pt_path),
        "size_mb": round(pt_path.stat().st_size / 1e6, 2),
        "backbone": "wide_resnet50_2",
    }
    verify_path.write_text(json.dumps(verify_data, indent=2))
    logger.info("Export verification saved: %s", verify_path)

    return pt_path


def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    checkpoint_path = project_root / "models" / "checkpoint.ckpt"
    output_dir = project_root / "models"

    if not checkpoint_path.exists():
        logger.error("Checkpoint not found at %s", checkpoint_path)
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    export_model(checkpoint_path, output_dir)


if __name__ == "__main__":
    main()
