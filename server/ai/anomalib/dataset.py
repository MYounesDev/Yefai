import logging
import shutil
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NORMAL_WEAR_MAX = 45
ANOMALY_WEAR_MIN = 90

DEFAULT_SPLIT = {
    "train": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "test": [13, 14, 15, 16, 17],
}


def classify_anomaly(wear_value: float) -> int | None:
    if wear_value <= NORMAL_WEAR_MAX:
        return 0
    if wear_value >= ANOMALY_WEAR_MIN:
        return 1
    return None


def find_image_path(labels_row: pd.Series, project_root: Path) -> Path | None:
    image_file = str(labels_row["ImageFile"])
    set_num = int(labels_row["Set"]) if pd.notna(labels_row.get("Set")) else None

    candidates = [
        project_root / image_file,
        project_root / "data" / image_file,
        project_root / "llm_docs" / image_file,
        project_root / "llm_docs" / image_file.replace("MATWI/", ""),
    ]

    if set_num is not None:
        set_dir = f"Set{set_num}"
        image_name = Path(image_file).name
        candidates.extend(
            [
                project_root / "data" / "MATWI" / set_dir / "images" / image_name,
                project_root / "data" / "MATWI" / set_dir / set_dir / "images" / image_name,
                project_root / "data" / "MATWI" / set_dir / image_name,
            ]
        )

    for c in candidates:
        if c.exists():
            return c
    return None


def resolve_image_paths(labels: pd.DataFrame, project_root: Path) -> pd.DataFrame:
    records = []
    nan_wear_count = 0
    nan_set_count = 0
    for _, row in labels.iterrows():
        img_path = find_image_path(row, project_root)
        if img_path is None:
            logger.warning("Image not found: %s", row["ImageFile"])
            continue

        wear_raw = row["wear"]
        if pd.isna(wear_raw):
            nan_wear_count += 1
            continue

        set_raw = row["Set"]
        if pd.isna(set_raw):
            nan_set_count += 1
            continue

        wear_val = float(wear_raw)
        set_val = int(set_raw)
        anomaly_label = classify_anomaly(wear_val)
        records.append(
            {
                "Set": set_val,
                "ImageFile": row["ImageFile"],
                "wear": wear_val,
                "anomaly_label": anomaly_label,
                "wear_type": str(row.get("wear_type", "unknown")),
                "path": img_path,
            }
        )

    if nan_wear_count > 0:
        logger.warning("Skipped %d rows with NaN wear values", nan_wear_count)
    if nan_set_count > 0:
        logger.warning("Skipped %d rows with NaN Set values", nan_set_count)

    return pd.DataFrame(records)


def build_anomalib_folder_structure(
    labels: pd.DataFrame,
    output_dir: Path,
    project_root: Path,
    splits: dict[str, list[int]] | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    if splits is None:
        splits = DEFAULT_SPLIT

    train_sets = set(splits.get("train", []))
    test_sets = set(splits.get("test", []))

    resolved = resolve_image_paths(labels, project_root)

    train_normal = resolved[resolved["Set"].isin(train_sets) & (resolved["anomaly_label"] == 0)]
    test_normal = resolved[resolved["Set"].isin(test_sets) & (resolved["anomaly_label"] == 0)]
    test_anomaly = resolved[resolved["Set"].isin(test_sets) & (resolved["anomaly_label"] == 1)]

    train_good_dir = output_dir / "train" / "good"
    test_good_dir = output_dir / "test" / "good"
    test_bad_dir = output_dir / "test" / "bad"

    for d in [train_good_dir, test_good_dir, test_bad_dir]:
        d.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}

    def copy_set(df: pd.DataFrame, dest_dir: Path, label: str):
        count = 0
        for _, row in df.iterrows():
            src = row["path"]
            dst = dest_dir / f"{row['Set']:02d}_{src.name}"
            if not dry_run:
                shutil.copy2(src, dst)
            count += 1
        counts[label] = count

    copy_set(train_normal, train_good_dir, "train/good")
    copy_set(test_normal, test_good_dir, "test/good")
    copy_set(test_anomaly, test_bad_dir, "test/bad")

    logger.info(
        "Anomalib dataset: train/good=%d, test/good=%d, test/bad=%d",
        counts.get("train/good", 0),
        counts.get("test/good", 0),
        counts.get("test/bad", 0),
    )

    mild_excluded = resolved[resolved["anomaly_label"].isna()]
    if len(mild_excluded) > 0:
        logger.info(
            "Mild wear images excluded from train/test: %d (45 < wear < 90)",
            len(mild_excluded),
        )

    return counts


def generate_dataset_report(
    labels: pd.DataFrame,
    output_dir: Path,
    project_root: Path,
    manifests_dir: Path | None = None,
) -> Path:
    resolved = resolve_image_paths(labels, project_root)
    report_path = output_dir / "anomalib_dataset_report.csv"
    resolved.to_csv(report_path, index=False)
    logger.info("Dataset report saved to %s", report_path)
    return report_path


def main():
    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent.parent
    project_root = server_root.parent

    labels_path = server_root / "dataset" / "labels.csv"
    manifests_dir = project_root / "data" / "manifests"
    output_dir = project_root / "data" / "anomalib_format"

    labels = pd.read_csv(labels_path)
    logger.info("Loaded %d rows from labels.csv", len(labels))

    build_anomalib_folder_structure(labels, output_dir, project_root)
    generate_dataset_report(labels, output_dir, project_root, manifests_dir)


if __name__ == "__main__":
    main()
