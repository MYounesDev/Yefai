import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

WEAR_TYPE_MAP = {
    "flank_wear": "flank_wear",
    "adhesion": "adhesion",
    "combination": "combination",
}


def classify_wear_type_from_labels(
    image_name: str,
    labels_df: pd.DataFrame,
) -> str:
    label_row = labels_df[labels_df["ImageFile"].str.contains(image_name, na=False)]
    if label_row.empty:
        return "unknown"
    row = label_row.iloc[0]
    wear_type = str(row.get("wear_type", row.get("type", "unknown"))).strip().lower()
    if not wear_type:
        return "unknown"
    for key, value in WEAR_TYPE_MAP.items():
        if key in wear_type or wear_type == key:
            return value
    return "unknown"


def classify_wear_type_batch(
    anomaly_results_df: pd.DataFrame,
    labels_df: pd.DataFrame,
) -> pd.DataFrame:
    types = []
    for _, row in anomaly_results_df.iterrows():
        wt = classify_wear_type_from_labels(row["image_name"], labels_df)
        types.append(wt)
    anomaly_results_df["wear_type"] = types

    distribution = anomaly_results_df["wear_type"].value_counts().to_dict()
    logger.info("Wear type distribution: %s", distribution)

    return anomaly_results_df


def compute_accuracy(
    results_df: pd.DataFrame,
    labels_df: pd.DataFrame,
) -> dict[str, object]:
    correct = 0
    total = 0
    confusion: dict[str, dict[str, int]] = {}

    for _, row in results_df.iterrows():
        predicted = row["wear_type"]
        actual = classify_wear_type_from_labels(row["image_name"], labels_df)

        confusion.setdefault(actual, {}).setdefault(predicted, 0)
        confusion[actual][predicted] += 1

        if predicted == actual and actual != "unknown":
            correct += 1
        if actual != "unknown":
            total += 1

    accuracy = correct / total if total > 0 else 0.0
    logger.info("Wear type classification accuracy: %.1f%% (%d/%d)", accuracy * 100, correct, total)
    return {"accuracy": accuracy, "correct": correct, "total": total, "confusion": confusion}


def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    results_path = project_root / "data" / "anomalib_inference_results.csv"
    labels_path = project_root / "server" / "dataset" / "labels.csv"

    if not results_path.exists():
        logger.error("Inference results not found at %s", results_path)
        return

    results_df = pd.read_csv(results_path)
    labels_df = pd.read_csv(labels_path)

    results_df = classify_wear_type_batch(results_df, labels_df)
    compute_accuracy(results_df, labels_df)

    output_path = project_root / "data" / "wear_classification_results.csv"
    results_df.to_csv(output_path, index=False)
    logger.info("Wear classification results saved to %s", output_path)


if __name__ == "__main__":
    main()
