import argparse
import gc
import logging
import time
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

from ai.embeddings.model import encode_image, get_device, load_jina_model, warmup_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_GPU_BATCH_SIZE = 32
DEFAULT_DB_BATCH_SIZE = 5
DEFAULT_EMBEDDING_DIM = 1024
DELAY_BETWEEN_BATCHES = 0.5


def find_all_images(
    root_dirs: list[Path], extensions: tuple = (".jpg", ".jpeg", ".png")
) -> list[Path]:
    images: list[Path] = []
    seen: set[str] = set()
    for root_dir in root_dirs:
        if not root_dir.exists():
            continue
        for ext in extensions:
            for img_path in root_dir.rglob(f"*{ext}"):
                key = str(img_path.resolve())
                if key not in seen:
                    images.append(img_path)
                    seen.add(key)
    logger.info("Found %d unique images", len(images))
    return images


def generate_embeddings(
    model,
    image_paths: list[Path],
    batch_size: int = DEFAULT_GPU_BATCH_SIZE,
    device: str | None = None,
    labels_df: pd.DataFrame | None = None,
) -> list[dict]:
    if device is None:
        device = get_device()

    results: list[dict] = []
    total = len(image_paths)
    failed = 0

    for i in range(0, total, batch_size):
        batch = image_paths[i : i + batch_size]
        for img_path in batch:
            image = None
            try:
                image = Image.open(img_path).convert("RGB")
                vector = encode_image(model, image, device)

                image_name = img_path.name
                label_row = None
                if labels_df is not None:
                    matching = labels_df[labels_df["ImageFile"].str.contains(image_name, na=False)]
                    if not matching.empty:
                        label_row = matching.iloc[0]

                results.append(
                    {
                        "image_name": image_name,
                        "image_path": str(img_path),
                        "vector": vector,
                        "dim": len(vector),
                        "set": int(label_row["Set"]) if label_row is not None else None,
                        "wear": float(label_row["wear"]) if label_row is not None else None,
                    }
                )
            except Exception as e:
                logger.warning("Failed to embed %s: %s", img_path.name, e)
                failed += 1
            finally:
                if image is not None:
                    image.close()

        gc.collect()

        if (i // batch_size) % 10 == 0:
            logger.info(
                "Progress: %d/%d images (failed: %d)", min(i + batch_size, total), total, failed
            )

    logger.info("Embedding complete: %d images, %d failed", len(results), failed)
    return results


def _build_label_lookup(labels_df: pd.DataFrame | None) -> dict[str, pd.Series]:
    if labels_df is None or "ImageFile" not in labels_df:
        return {}
    lookup: dict[str, pd.Series] = {}
    for _, row in labels_df.iterrows():
        image_file = row.get("ImageFile")
        if pd.isna(image_file):
            continue
        lookup[Path(str(image_file)).name] = row
    return lookup


def _embedding_row(
    img_path: Path,
    vector: list[float],
    project_root: Path,
    label_lookup: dict[str, pd.Series],
) -> dict[str, Any]:
    label_row = label_lookup.get(img_path.name)
    set_value = None
    wear_value = None
    if label_row is not None:
        if pd.notna(label_row.get("Set")):
            set_value = int(label_row["Set"])
        if pd.notna(label_row.get("wear")):
            wear_value = float(label_row["wear"])

    try:
        file_path = str(img_path.relative_to(project_root))
    except ValueError:
        file_path = str(img_path)

    image_name = f"Set{set_value}/{img_path.name}" if set_value else img_path.name

    return {
        "image_name": image_name,
        "file_path": file_path,
        "image_path": str(img_path),
        "image_embedding": vector,
        "set": set_value,
        "wear": wear_value,
        "metadata": {"embedding_source": "jinaai/jina-clip-v2"},
    }


def write_image_embeddings_streaming(
    model,
    image_paths: list[Path],
    project_root: Path,
    labels_df: pd.DataFrame | None = None,
    db_batch_size: int = DEFAULT_DB_BATCH_SIZE,
    delay: float = DELAY_BETWEEN_BATCHES,
    limit: int = 0,
) -> tuple[int, int]:
    from db.client import get_supabase_client

    client = get_supabase_client()
    if client is None:
        logger.warning("Supabase client not available — skipping DB write")
        return 0, len(image_paths)

    device = get_device()
    label_lookup = _build_label_lookup(labels_df)

    paths = image_paths[:limit] if limit > 0 else image_paths
    total = len(paths)
    written = 0
    failed = 0
    rows: list[dict[str, Any]] = []

    logger.info(
        "Starting streaming embed — total=%d, db_batch_size=%d, delay=%.1fs",
        total,
        db_batch_size,
        delay,
    )

    for index, img_path in enumerate(paths, start=1):
        image = None
        try:
            image = Image.open(img_path).convert("RGB")
            vector = encode_image(model, image, device)
            if len(vector) != DEFAULT_EMBEDDING_DIM:
                raise ValueError(f"unexpected embedding dim {len(vector)}")
            rows.append(_embedding_row(img_path, vector, project_root, label_lookup))
        except Exception as e:
            logger.warning("Failed to embed %s: %s", img_path.name, e)
            failed += 1
        finally:
            if image is not None:
                image.close()

        if rows and (len(rows) >= db_batch_size or index == total):
            try:
                seen_names: set[str] = set()
                deduped = []
                for row in rows:
                    name = row["image_name"]
                    if name in seen_names:
                        continue
                    seen_names.add(name)
                    deduped.append(row)
                client.table("images").upsert(deduped, on_conflict="image_name").execute()
                written += len(deduped)
                logger.info(
                    "DB upsert %d/%d — batch=%d, written=%d, failed=%d",
                    index,
                    total,
                    len(deduped),
                    written,
                    failed,
                )
            except Exception as e:
                logger.error("DB upsert failed at image %d: %s", index, e)
                failed += len(rows)
            finally:
                rows = []
                gc.collect()
                if index < total:
                    time.sleep(delay)

    logger.info("Embedding DB write complete: %d written, %d failed", written, failed)
    gc.collect()
    return written, failed


def write_embeddings_to_supabase(
    embeddings: list[dict],
    batch_size: int = DEFAULT_DB_BATCH_SIZE,
    delay: float = DELAY_BETWEEN_BATCHES,
):
    try:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            logger.warning("Supabase client not available — skipping DB write")
            return

        total = len(embeddings)
        for i in range(0, total, batch_size):
            batch = embeddings[i : i + batch_size]
            rows = []
            seen_names: set[str] = set()
            for emb in batch:
                name = emb["image_name"]
                if name in seen_names:
                    continue
                seen_names.add(name)
                rows.append(
                    {
                        "image_name": emb["image_name"],
                        "file_path": emb["image_path"],
                        "image_path": emb["image_path"],
                        "image_embedding": emb["vector"],
                        "set": emb.get("set"),
                        "wear": emb.get("wear"),
                        "metadata": {"embedding_source": "jinaai/jina-clip-v2"},
                    }
                )
            client.table("images").upsert(rows, on_conflict="image_name").execute()
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            logger.info(
                "Embedding upsert batch %d/%d (%d records) — OK",
                batch_num,
                total_batches,
                len(rows),
            )
            gc.collect()
            if i + batch_size < total:
                time.sleep(delay)

        logger.info("Wrote %d embeddings to Supabase images table", total)
        gc.collect()
    except ImportError:
        logger.warning("Supabase SDK not available — skipping DB write")
    except Exception as e:
        logger.error("Failed to write embeddings to Supabase: %s", e)


def main():
    parser = argparse.ArgumentParser(description="Batch embed MATWI images with Jina CLIP v2")
    parser.add_argument(
        "--db-batch-size",
        type=int,
        default=DEFAULT_DB_BATCH_SIZE,
        help=f"Records per Supabase upsert (default: {DEFAULT_DB_BATCH_SIZE})",
    )
    parser.add_argument(
        "--gpu-batch-size",
        type=int,
        default=DEFAULT_GPU_BATCH_SIZE,
        help=f"Images per GPU inference batch (default: {DEFAULT_GPU_BATCH_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DELAY_BETWEEN_BATCHES,
        help=f"Delay between batches in seconds (default: {DELAY_BETWEEN_BATCHES}s)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process first N images (0 = all, for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate embeddings but skip Supabase write",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    server_root = project_root / "server"
    data_root = project_root / "data"

    matwi_dir = data_root / "MATWI"
    anomalib_dir = data_root / "anomalib_format"

    labels_path = server_root / "dataset" / "labels.csv"
    labels_df = pd.read_csv(labels_path) if labels_path.exists() else None

    logger.info("Loading Jina CLIP v2 model...")
    model = load_jina_model()
    warmup_model(model)
    logger.info("Model loaded and warmed up")

    image_dirs = [matwi_dir, anomalib_dir]
    images = find_all_images(image_dirs)
    logger.info("Total images to embed: %d", len(images))

    if args.dry_run:
        logger.info("Dry run mode — skipping Supabase write")
        embeddings = generate_embeddings(
            model,
            images[: args.limit] if args.limit > 0 else images,
            batch_size=args.gpu_batch_size,
            labels_df=labels_df,
        )
        logger.info("Dry run complete: %d embeddings generated", len(embeddings))
    else:
        written, failed = write_image_embeddings_streaming(
            model,
            images,
            project_root=project_root,
            labels_df=labels_df,
            db_batch_size=args.db_batch_size,
            delay=args.delay,
            limit=args.limit,
        )

        output_path = data_root / "embeddings.json"
        import json

        output_path.write_text(
            json.dumps(
                {
                    "model": "jinaai/jina-clip-v2",
                    "dim": DEFAULT_EMBEDDING_DIM,
                    "total_images": len(images),
                    "written": written,
                    "failed": failed,
                },
                indent=2,
            )
        )
        logger.info("Embedding metadata saved to %s", output_path)


if __name__ == "__main__":
    main()
