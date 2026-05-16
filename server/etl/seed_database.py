import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def resolve_paths(
    labels_path: Optional[str] = None,
) -> tuple[Path, Path]:
    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent
    project_root = server_root.parent

    lp = Path(labels_path) if labels_path else server_root / "dataset" / "labels.csv"
    output_dir = project_root / "data" / "seed"

    return lp, output_dir


def prepare_set_records(labels: pd.DataFrame) -> List[Dict]:
    records = []
    for set_id in sorted(labels["Set"].unique()):
        set_df = labels[labels["Set"] == set_id]
        records.append(
            {
                "name": f"Set{set_id}",
                "image_count": int(len(set_df)),
            }
        )
    logger.info("Prepared %d set records", len(records))
    return records


def prepare_image_records(labels: pd.DataFrame) -> List[Dict]:
    records = []
    for _, row in labels.iterrows():
        wear_type = row.get("wear_type", row.get("type", "unknown"))
        if isinstance(wear_type, str) and "flank" in wear_type and "adhesion" in wear_type:
            wear_type = "combination"

        flank = None
        adhesive = None
        combination = None
        if wear_type == "flank_wear":
            flank = float(row["wear"])
        elif wear_type == "adhesion":
            adhesive = float(row["wear"])
        elif wear_type == "combination":
            combination = float(row["wear"])

        ts = row.get("ImageDateTime", row.get("timestamp"))
        if pd.notna(ts):
            ts = pd.Timestamp(ts).isoformat()

        records.append(
            {
                "set_id": int(row["Set"]),
                "file_path": str(row["ImageFile"]),
                "flank_wear": flank,
                "adhesive_wear": adhesive,
                "combination_wear": combination,
                "wear_type": wear_type,
                "wear": float(row["wear"]),
                "timestamp": ts,
            }
        )

    logger.info("Prepared %d image records", len(records))
    return records


def seed_local_csv(
    set_records: List[Dict],
    image_records: List[Dict],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(set_records).to_csv(output_dir / "sets.csv", index=False)
    pd.DataFrame(image_records).to_csv(output_dir / "images.csv", index=False)
    logger.info("Seed data exported to %s", output_dir)


def seed_supabase(
    set_records: List[Dict],
    image_records: List[Dict],
) -> bool:
    try:
        from db.client import get_supabase_client
    except ImportError:
        logger.warning("db.client module not available — skipping Supabase seed")
        return False

    client = get_supabase_client()
    if client is None:
        logger.warning("Supabase client not available — skipping live seed")
        return False

    try:
        for i in range(0, len(set_records), BATCH_SIZE):
            batch = set_records[i : i + BATCH_SIZE]
            client.table("sets").insert(batch).execute()
        logger.info("Seeded %d set(s) to Supabase", len(set_records))

        for i in range(0, len(image_records), BATCH_SIZE):
            batch = image_records[i : i + BATCH_SIZE]
            client.table("images").insert(batch).execute()
        logger.info("Seeded %d image(s) to Supabase", len(image_records))

        return True
    except Exception as e:
        logger.error("Supabase seed failed: %s", e)
        return False


def print_summary(set_records: List[Dict], image_records: List[Dict]) -> None:
    total_sets = len(set_records)
    total_images = len(image_records)
    wear_types: Dict[str, int] = {}
    for r in image_records:
        wt = r["wear_type"]
        wear_types[wt] = wear_types.get(wt, 0) + 1

    logger.info("==== Seed Summary ====")
    logger.info("Total sets: %d", total_sets)
    logger.info("Total images: %d", total_images)
    for wt, count in sorted(wear_types.items()):
        logger.info("  %s: %d (%.1f%%)", wt, count, 100 * count / total_images)


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase with MATWI metadata")
    parser.add_argument("--labels-path", default=None, help="Path to labels.csv")
    parser.add_argument("--local-only", action="store_true", help="Only export CSV, skip Supabase")
    args = parser.parse_args()

    labels_path, output_dir = resolve_paths(args.labels_path)
    labels = pd.read_csv(labels_path)

    from etl.parse_labels import normalize_wear_type
    labels["wear_type"] = labels["type"].apply(normalize_wear_type)

    set_records = prepare_set_records(labels)
    image_records = prepare_image_records(labels)

    seed_local_csv(set_records, image_records, output_dir)
    print_summary(set_records, image_records)

    if not args.local_only:
        seed_supabase(set_records, image_records)


if __name__ == "__main__":
    main()
