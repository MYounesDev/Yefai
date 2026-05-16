import argparse
import logging
import os
import zipfile
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def resolve_data_root() -> Path:
    env_root = os.environ.get("YEFAI_DATA_ROOT", "")
    if env_root:
        return Path(env_root)
    return Path(__file__).resolve().parent.parent.parent / "data"


def extract_zips(dataset_dir: Path, output_dir: Path) -> dict[str, int]:
    zip_files = sorted(dataset_dir.glob("Set*.zip"))
    if not zip_files:
        logger.warning("No Set*.zip files found in %s", dataset_dir)
        return {}

    extracted_counts: dict[str, int] = {}
    output_dir.mkdir(parents=True, exist_ok=True)

    for zpath in zip_files:
        set_name = zpath.stem
        target = output_dir / set_name
        target.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(target)

        image_dir = target / "images"
        if not image_dir.exists():
            inner_matwi = target / "MATWI" / set_name / "images"
            if inner_matwi.exists():
                image_dir = inner_matwi
            else:
                candidates = list(target.glob("**/images"))
                if candidates:
                    image_dir = candidates[0]
        image_count = len(list(image_dir.glob("*"))) if image_dir.exists() else 0
        extracted_counts[set_name] = image_count
        logger.info("Extracted %s → %d images", set_name, image_count)

    return extracted_counts


def verify_against_labels(extracted_counts: dict[str, int], labels_path: Path) -> bool:
    if not labels_path.exists():
        logger.error("labels.csv not found at %s", labels_path)
        return False

    labels = pd.read_csv(labels_path)
    label_counts = labels.groupby("Set").size()

    total_label_images = len(labels)
    total_extracted = sum(extracted_counts.values())

    logger.info("labels.csv total images: %d", total_label_images)
    logger.info("Extracted total images: %d", total_extracted)

    if total_extracted != total_label_images:
        logger.error(
            "MISMATCH: %d in labels.csv vs %d extracted",
            total_label_images,
            total_extracted,
        )
        return False

    for set_id in label_counts.index:
        set_name = f"Set{set_id}"
        label_count = label_counts[set_id]
        extracted = extracted_counts.get(set_name, 0)
        if label_count != extracted:
            logger.error(
                "Set %d mismatch: %d labels vs %d extracted",
                set_id,
                label_count,
                extracted,
            )

    logger.info("All sets verified against labels.csv")
    return True


def main():
    parser = argparse.ArgumentParser(description="Extract MATWI dataset zip files")
    parser.add_argument(
        "--dataset-dir",
        default=None,
        help="Path to directory containing Set*.zip files",
    )
    parser.add_argument("--output-dir", default=None, help="Output directory")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent
    data_root = resolve_data_root()

    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else server_root / "dataset"
    output_dir = Path(args.output_dir) if args.output_dir else data_root / "MATWI"
    labels_path = dataset_dir / "labels.csv"

    logger.info("Dataset dir: %s", dataset_dir)
    logger.info("Output dir: %s", output_dir)

    counts = extract_zips(dataset_dir, output_dir)
    if not counts:
        logger.error("No zip files extracted")
        return

    ok = verify_against_labels(counts, labels_path)
    if not ok:
        logger.error("Verification failed — check dataset integrity")


if __name__ == "__main__":
    main()
