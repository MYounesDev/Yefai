import json
import logging
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NORMAL_WEAR_MAX = 45
ANOMALY_WEAR_MIN = 90
TRAIN_SETS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
BATCH_SIZE = 64


def compute_channel_stats(image_paths: list[Path], batch_size: int = BATCH_SIZE) -> dict:
    channel_sum = np.zeros(3, dtype=np.float64)
    channel_sum_sq = np.zeros(3, dtype=np.float64)
    pixel_count = 0
    valid = 0

    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i : i + batch_size]
        for img_path in batch:
            try:
                img = Image.open(img_path).convert("RGB")
                arr = np.array(img, dtype=np.float64) / 255.0
                h, w, c = arr.shape
                channel_sum += arr.sum(axis=(0, 1))
                channel_sum_sq += (arr**2).sum(axis=(0, 1))
                pixel_count += h * w
                valid += 1
            except Exception as e:
                logger.warning("Skipping %s: %s", img_path.name, e)

        if i % (batch_size * 10) == 0:
            logger.debug(
                "Stats progress: %d/%d images",
                min(i + batch_size, len(image_paths)),
                len(image_paths),
            )

    if valid == 0:
        raise ValueError("No valid images found for statistics computation")

    mean = channel_sum / pixel_count
    std = np.sqrt(channel_sum_sq / pixel_count - mean**2)

    stats = {
        "mean": [round(float(mean[0]), 6), round(float(mean[1]), 6), round(float(mean[2]), 6)],
        "std": [round(float(std[0]), 6), round(float(std[1]), 6), round(float(std[2]), 6)],
        "source": "MATWI training set (normal images only)",
        "n_images": valid,
        "n_pixels": int(pixel_count),
        "image_size": f"{h}x{w}" if valid > 0 else "unknown",
    }

    logger.info(
        "Computed stats from %d images: mean=%s, std=%s", valid, stats["mean"], stats["std"]
    )
    return stats


def find_train_normal_images(labels: pd.DataFrame, project_root: Path) -> list[Path]:
    image_paths: list[Path] = []
    skipped_nan = 0
    skipped_mild = 0
    skipped_anomaly = 0
    skipped_not_found = 0
    skipped_wrong_set = 0

    for _, row in labels.iterrows():
        set_id = row["Set"]
        if pd.isna(set_id):
            continue
        set_id = int(set_id)

        if set_id not in TRAIN_SETS:
            skipped_wrong_set += 1
            continue

        wear_val = row["wear"]
        if pd.isna(wear_val):
            skipped_nan += 1
            continue

        wear_val = float(wear_val)

        if wear_val > NORMAL_WEAR_MAX:
            if wear_val >= ANOMALY_WEAR_MIN:
                skipped_anomaly += 1
            else:
                skipped_mild += 1
            continue

        image_file = str(row["ImageFile"])
        set_dir = f"Set{set_id}"
        image_name = Path(image_file).name
        for candidate in [
            project_root / image_file,
            project_root / "data" / image_file,
            project_root / "llm_docs" / image_file,
            project_root / "llm_docs" / image_file.replace("MATWI/", ""),
            project_root / "data" / "MATWI" / set_dir / "images" / image_name,
            project_root / "data" / "MATWI" / set_dir / set_dir / "images" / image_name,
            project_root / "data" / "MATWI" / set_dir / image_name,
        ]:
            if candidate.exists():
                image_paths.append(candidate)
                break
        else:
            skipped_not_found += 1

    logger.info(
        "Train normal images found: %d (skipped: nan=%d, mild=%d, anomaly=%d, "
        "wrong_set=%d, not_found=%d)",
        len(image_paths),
        skipped_nan,
        skipped_mild,
        skipped_anomaly,
        skipped_wrong_set,
        skipped_not_found,
    )
    return image_paths


def compute_normalization_stats(
    labels_path: Path,
    output_path: Path,
    project_root: Path | None = None,
) -> dict:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent.parent

    labels = pd.read_csv(labels_path)
    logger.info("Loaded %d rows from %s", len(labels), labels_path)

    train_normal = find_train_normal_images(labels, project_root)

    if len(train_normal) == 0:
        raise ValueError("No train normal images found — check labels.csv and data paths")

    stats = compute_channel_stats(train_normal)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stats, indent=2))
    logger.info("Normalization stats saved to %s", output_path)

    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]
    logger.info(
        "Comparison — ImageNet: mean=%s std=%s | MATWI normal: mean=%s std=%s",
        imagenet_mean,
        imagenet_std,
        stats["mean"],
        stats["std"],
    )

    return stats


def load_normalization_stats(stats_path: Path) -> dict[str, Any]:
    stats = json.loads(stats_path.read_text())
    if not isinstance(stats, dict):
        raise ValueError(f"Normalization stats must be a JSON object: {stats_path}")
    return cast(dict[str, Any], stats)


def main():
    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent.parent
    project_root = server_root.parent

    labels_path = server_root / "dataset" / "labels.csv"
    output_path = project_root / "data" / "normalization_stats.json"

    compute_normalization_stats(labels_path, output_path, project_root)


if __name__ == "__main__":
    main()
