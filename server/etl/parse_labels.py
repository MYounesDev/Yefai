import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def normalize_wear_type(raw_type) -> str:
    if not isinstance(raw_type, str) or not raw_type.strip():
        return "unknown"
    t = raw_type.strip().lower()
    if t == "flank_wear":
        return "flank_wear"
    if "adhesion" in t and "flank" in t:
        return "combination"
    if t == "adhesion":
        return "adhesion"
    return t


def parse_labels(labels_path: Path) -> pd.DataFrame:
    df = pd.read_csv(labels_path)

    required = {"ImageFile", "wear", "type", "Set", "ImageDateTime"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"labels.csv missing columns: {missing}")

    df["wear"] = pd.to_numeric(df["wear"], errors="coerce").astype(float)
    df["ImageDateTime"] = pd.to_datetime(df["ImageDateTime"], errors="coerce")
    df["Set"] = pd.to_numeric(df["Set"], errors="coerce").astype(int)
    df["wear_type"] = df["type"].apply(normalize_wear_type)

    df["ImageFile"] = df["ImageFile"].astype(str)

    if "SensorFile" in df.columns:
        df["SensorFile"] = df["SensorFile"].astype(str)

    if "SensorDateTime" in df.columns:
        df["SensorDateTime"] = pd.to_datetime(df["SensorDateTime"], errors="coerce")

    null_wear = df["wear"].isna().sum()
    null_time = df["ImageDateTime"].isna().sum()
    if null_wear > 0:
        logger.warning("Null wear values: %d", null_wear)
    if null_time > 0:
        logger.warning("Null datetime values: %d", null_time)

    logger.info("Parsed %d rows from labels.csv", len(df))
    logger.info("Wear types: %s", df["wear_type"].value_counts().to_dict())
    return df


def parse_sets(sets_path: Path) -> pd.DataFrame:
    df = pd.read_csv(sets_path)

    rename_map = {}
    for col in df.columns:
        stripped = str(col).strip()
        if stripped and stripped != col:
            rename_map[col] = stripped
    if rename_map:
        df = df.rename(columns=rename_map)

    first_col = df.columns[0]
    if str(first_col).strip() == "" or "Unnamed" in str(first_col):
        df = df.rename(columns={first_col: "Set"})

    df["Set"] = df["Set"].astype(str).str.extract(r"(\d+)", expand=False)
    df["Set"] = pd.to_numeric(df["Set"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Set"])
    df["Set"] = df["Set"].astype(int)

    logger.info("Parsed %d rows from sets.csv", len(df))
    return df


def parse_metadata(labels_path: Path, sets_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = parse_labels(labels_path)
    sets = parse_sets(sets_path)

    label_sets = set(labels["Set"].unique())
    meta_sets = set(sets["Set"].unique())
    missing_in_meta = label_sets - meta_sets
    if missing_in_meta:
        logger.warning("Sets in labels but not in sets.csv: %s", missing_in_meta)

    return labels, sets
