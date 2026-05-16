import argparse
import gc
import logging
import math
import time
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 25
DELAY_BETWEEN_BATCHES = 0.5


def resolve_paths(
    labels_path: str | None = None,
) -> tuple[Path, Path]:
    script_dir = Path(__file__).resolve().parent
    server_root = script_dir.parent
    project_root = server_root.parent

    lp = Path(labels_path) if labels_path else server_root / "dataset" / "labels.csv"
    output_dir = project_root / "data" / "seed"

    return lp, output_dir


def prepare_set_records(labels: pd.DataFrame) -> list[dict]:
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


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


def prepare_image_records(labels: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in labels.iterrows():
        wear_type = row.get("wear_type", row.get("type", "unknown"))
        if isinstance(wear_type, str) and "flank" in wear_type and "adhesion" in wear_type:
            wear_type = "combination"

        wear_val = _safe_float(row["wear"])

        flank = None
        adhesive = None
        combination = None
        if wear_type == "flank_wear":
            flank = wear_val
        elif wear_type == "adhesion":
            adhesive = wear_val
        elif wear_type == "combination":
            combination = wear_val

        ts = row.get("ImageDateTime", row.get("timestamp"))
        if pd.notna(ts):
            ts = pd.Timestamp(ts).isoformat()

            records.append(
                {
                    "image_name": f"Set{int(row['Set'])}/{Path(str(row['ImageFile'])).name}",
                    "set_id": int(row["Set"]),
                    "file_path": str(row["ImageFile"]),
                    "flank_wear": flank,
                    "adhesive_wear": adhesive,
                    "combination_wear": combination,
                    "wear_type": wear_type,
                    "wear": wear_val,
                    "timestamp": ts,
                }
            )

    logger.info("Prepared %d image records", len(records))
    return records


def seed_local_csv(
    set_records: list[dict],
    image_records: list[dict],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(set_records).to_csv(output_dir / "sets.csv", index=False)
    pd.DataFrame(image_records).to_csv(output_dir / "images.csv", index=False)
    logger.info("Seed data exported to %s", output_dir)


def seed_supabase(
    set_records: list[dict],
    image_records: list[dict],
    batch_size: int = BATCH_SIZE,
    delay: float = DELAY_BETWEEN_BATCHES,
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
        total_sets = len(set_records)
        set_batches = (total_sets + batch_size - 1) // batch_size
        for i in range(0, total_sets, batch_size):
            batch = set_records[i : i + batch_size]
            client.table("sets").upsert(batch, on_conflict="name").execute()
            batch_num = i // batch_size + 1
            logger.info(
                "Sets batch %d/%d (%d records) — OK",
                batch_num,
                set_batches,
                len(batch),
            )
            gc.collect()
            if i + batch_size < total_sets:
                time.sleep(delay)

        logger.info("Seeded %d set(s) to Supabase", total_sets)
        gc.collect()

        set_name_to_db_id: dict[str, int] = {}
        resp = client.table("sets").select("id,name").execute()
        if resp.data:
            for row in resp.data:
                set_name_to_db_id[row["name"]] = int(row["id"])
        logger.info("Fetched %d set ID(s) from Supabase", len(set_name_to_db_id))

        mapped_records = []
        for rec in image_records:
            set_name = f"Set{rec['set_id']}"
            db_id = set_name_to_db_id.get(set_name)
            if db_id is None:
                logger.warning(
                    "No DB id for set %s, skipping image %s", set_name, rec.get("image_name")
                )
                continue
            rec["set_id"] = db_id
            mapped_records.append(rec)

        logger.info(
            "Mapped %d image records (skipped %d)",
            len(mapped_records),
            len(image_records) - len(mapped_records),
        )

        total_images = len(mapped_records)
        image_batches = (total_images + batch_size - 1) // batch_size
        for i in range(0, total_images, batch_size):
            batch = mapped_records[i : i + batch_size]
            seen: set[str] = set()
            deduped = []
            dupes = 0
            for rec in batch:
                name = rec["image_name"]
                if name in seen:
                    dupes += 1
                    continue
                seen.add(name)
                deduped.append(rec)
            if dupes:
                logger.warning(
                    "Batch %d: dropped %d duplicate image_name(s)", i // batch_size + 1, dupes
                )
            client.table("images").upsert(deduped, on_conflict="image_name").execute()
            batch_num = i // batch_size + 1
            logger.info(
                "Images batch %d/%d (%d records) — OK",
                batch_num,
                image_batches,
                len(deduped),
            )
            gc.collect()
            if i + batch_size < total_images:
                time.sleep(delay)

        logger.info("Seeded %d image(s) to Supabase", total_images)
        gc.collect()

        return True
    except Exception as e:
        logger.error("Supabase seed failed: %s", e)
        return False


def print_summary(set_records: list[dict], image_records: list[dict]) -> None:
    total_sets = len(set_records)
    total_images = len(image_records)
    wear_types: dict[str, int] = {}
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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Records per Supabase insert batch (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DELAY_BETWEEN_BATCHES,
        help=f"Delay in seconds between batches (default: {DELAY_BETWEEN_BATCHES}s)",
    )
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
        logger.info(
            "Starting Supabase seed — batch_size=%d, delay=%.1fs",
            args.batch_size,
            args.delay,
        )
        seed_supabase(set_records, image_records, batch_size=args.batch_size, delay=args.delay)


if __name__ == "__main__":
    main()
