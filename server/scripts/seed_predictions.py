"""Seed anomalies table with wear prediction data from images table.

Reads images (wear, timestamp, set_id) and inserts into anomalies
with estimated_wear_um and machine_id for the prediction pipeline.

Usage:
    python server/scripts/seed_predictions.py
    python server/scripts/seed_predictions.py --batch-size 50 --dry-run
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 100
DELAY_BETWEEN_BATCHES = 0.3


def fetch_images(client, dry_run: bool = False) -> list[dict]:
    logger.info("Fetching images with wear data from Supabase...")
    resp = (
        client.table("images")
        .select("id,set_id,wear,wear_type,timestamp,image_name")
        .not_.is_("wear", "null")
        .execute()
    )

    if not resp.data:
        logger.warning("No images with wear data found")
        return []

    logger.info("Fetched %d images with wear data", len(resp.data))

    set_name_map = _fetch_set_names(client)

    for img in resp.data:
        set_id = img["set_id"]
        img["set_name"] = set_name_map.get(set_id, f"Set{set_id}")

    return resp.data


def _fetch_set_names(client) -> dict[int, str]:
    resp = client.table("sets").select("id,name").execute()
    if not resp.data:
        return {}
    return {int(row["id"]): row["name"] for row in resp.data}


def build_anomaly_records(images: list[dict]) -> list[dict]:
    records = []
    skipped_no_timestamp = 0

    for img in images:
        ts = img.get("timestamp")
        if not ts:
            skipped_no_timestamp += 1
            continue

        records.append(
            {
                "image_id": img["id"],
                "machine_id": img.get("set_name", f"Set{img['set_id']}"),
                "estimated_wear_um": img["wear"],
                "wear_type": img.get("wear_type"),
                "score": 0.0,
                "detected_at": ts,
            }
        )

    if skipped_no_timestamp:
        logger.info("Skipped %d images without timestamp", skipped_no_timestamp)

    return records


def upsert_anomalies(
    client,
    records: list[dict],
    batch_size: int = BATCH_SIZE,
    delay: float = DELAY_BETWEEN_BATCHES,
    dry_run: bool = False,
) -> int:
    if dry_run:
        for r in records[:5]:
            logger.info(
                "  [DRY-RUN] image_id=%s machine=%s wear=%.1fµm ts=%s",
                r["image_id"],
                r["machine_id"],
                r["estimated_wear_um"],
                r["detected_at"],
            )
        logger.info("DRY RUN: would seed %d records", len(records))
        return len(records)

    total = len(records)
    batches = (total + batch_size - 1) // batch_size

    for i in range(0, total, batch_size):
        batch = records[i : i + batch_size]
        image_ids = [r["image_id"] for r in batch]

        client.table("anomalies").delete().in_("image_id", image_ids).execute()

        client.table("anomalies").insert(batch).execute()
        batch_num = i // batch_size + 1
        logger.info(
            "Batch %d/%d (%d records) OK",
            batch_num,
            batches,
            len(batch),
        )
        if i + batch_size < total:
            time.sleep(delay)

    return total


def main():
    parser = argparse.ArgumentParser(
        description="Seed anomalies table with wear prediction data from images"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Records per batch (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DELAY_BETWEEN_BATCHES,
        help=f"Delay between batches in seconds (default: {DELAY_BETWEEN_BATCHES})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing to Supabase",
    )
    args = parser.parse_args()

    from db.client import get_supabase_client

    client = get_supabase_client()
    if client is None:
        logger.error("Supabase client not available. Check .env configuration.")
        sys.exit(1)

    images = fetch_images(client, dry_run=args.dry_run)
    if not images:
        logger.info("No data to seed")
        return

    records = build_anomaly_records(images)
    logger.info("Built %d anomaly records from %d images", len(records), len(images))

    _ = upsert_anomalies(
        client,
        records,
        batch_size=args.batch_size,
        delay=args.delay,
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        # Verify
        resp = (
            client.table("anomalies")
            .select("id", count="exact")
            .not_.is_("estimated_wear_um", "null")
            .execute()
        )
        logger.info("Verification: %d anomalies with estimated_wear_um", resp.count)

        # Show per-machine stats
        resp = client.table("anomalies").select("machine_id").execute()
        if resp.data:
            machines: dict[str, int] = {}
            for row in resp.data:
                mid = row.get("machine_id", "unknown")
                machines[mid] = machines.get(mid, 0) + 1
            logger.info("Per-machine anomaly counts:")
            for mid in sorted(machines.keys()):
                logger.info("  %s: %d records", mid, machines[mid])


if __name__ == "__main__":
    main()
