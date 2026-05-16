import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_SPLIT = {
    "train": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "test": [13, 14, 15, 16, 17],
}


def build_split_manifest(
    labels: pd.DataFrame,
    splits: dict[str, list[int]],
) -> pd.DataFrame:
    train_ids = set(splits.get("train", []))
    test_ids = set(splits.get("test", []))
    overlap = train_ids & test_ids
    if overlap:
        raise ValueError(f"Split overlap detected: sets {overlap} in both train and test")

    records = []
    for set_id in sorted(labels["Set"].unique()):
        set_df = labels[labels["Set"] == set_id]
        image_count = len(set_df)

        if set_id in train_ids:
            split = "train"
        elif set_id in test_ids:
            split = "test"
        else:
            split = "unassigned"
            logger.warning("Set %d not in any split", set_id)

        records.append(
            {
                "Set": int(set_id),
                "ImageCount": image_count,
                "Split": split,
            }
        )

    manifest = pd.DataFrame(records)
    return manifest


def validate_split_no_leakage(manifest: pd.DataFrame, labels: pd.DataFrame) -> bool:
    train_sets = set(manifest[manifest["Split"] == "train"]["Set"])
    test_sets = set(manifest[manifest["Split"] == "test"]["Set"])

    overlap = train_sets & test_sets
    if overlap:
        logger.error("LEAKAGE: sets in both train and test: %s", overlap)
        return False

    all_assigned = train_sets | test_sets
    unassigned = set(manifest["Set"]) - all_assigned
    if unassigned:
        logger.warning("Unassigned sets: %s", unassigned)

    return True


def validate_split_ratio(manifest: pd.DataFrame) -> bool:
    train_count = manifest[manifest["Split"] == "train"]["ImageCount"].sum()
    test_count = manifest[manifest["Split"] == "test"]["ImageCount"].sum()
    total = train_count + test_count

    if total == 0:
        logger.error("No images in manifest")
        return False

    ratio = train_count / total
    logger.info(
        "Split ratio: train=%.1f%% (%d images), test=%.1f%% (%d images)",
        ratio * 100,
        train_count,
        (1 - ratio) * 100,
        test_count,
    )

    if not (0.67 <= ratio <= 0.73):
        logger.warning("Split ratio outside 70%% ± 3%% tolerance")
        return False

    return True


def generate_split(
    labels_path: Path,
    output_dir: Path,
    splits: dict[str, list[int]] | None = None,
) -> pd.DataFrame:
    labels = pd.read_csv(labels_path)

    if splits is None:
        splits = DEFAULT_SPLIT

    manifest = build_split_manifest(labels, splits)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output_dir / "split_manifest.csv", index=False)
    logger.info("Split manifest saved to %s", output_dir / "split_manifest.csv")

    if not validate_split_no_leakage(manifest, labels):
        raise ValueError("Split leakage detected")

    validate_split_ratio(manifest)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate train/test split manifest")
    parser.add_argument(
        "--labels-path",
        default=None,
        help="Path to labels.csv",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for split manifest",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent
    project_root = server_root.parent

    labels_path = (
        Path(args.labels_path) if args.labels_path else server_root / "dataset" / "labels.csv"
    )
    output_dir = Path(args.output_dir) if args.output_dir else project_root / "data" / "manifests"

    generate_split(labels_path, output_dir)


if __name__ == "__main__":
    main()
