import logging
from pathlib import Path

import pandas as pd
from PIL import Image

from ai.embeddings.model import encode_image, get_device, load_jina_model, warmup_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 32
DEFAULT_EMBEDDING_DIM = 1024


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
                name = img_path.name.lower()
                if name not in seen:
                    images.append(img_path)
                    seen.add(name)
    logger.info("Found %d unique images", len(images))
    return images


def generate_embeddings(
    model,
    image_paths: list[Path],
    batch_size: int = DEFAULT_BATCH_SIZE,
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

        if (i // batch_size) % 10 == 0:
            logger.info(
                "Progress: %d/%d images (failed: %d)", min(i + batch_size, total), total, failed
            )

    logger.info("Embedding complete: %d images, %d failed", len(results), failed)
    return results


def write_embeddings_to_supabase(
    embeddings: list[dict],
):
    try:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            logger.warning("Supabase client not available — skipping DB write")
            return

        batch_size = 50
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i : i + batch_size]
            rows = []
            for emb in batch:
                rows.append(
                    {
                        "image_name": emb["image_name"],
                        "image_embedding": emb["vector"],
                        "set": emb.get("set"),
                        "wear": emb.get("wear"),
                    }
                )
            client.table("images").upsert(rows).execute()

        logger.info("Wrote %d embeddings to Supabase images table", len(embeddings))
    except ImportError:
        logger.warning("Supabase SDK not available — skipping DB write")
    except Exception as e:
        logger.error("Failed to write embeddings to Supabase: %s", e)


def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    server_root = project_root / "server"
    data_root = project_root / "data"

    matwi_dir = data_root / "MATWI"
    anomalib_dir = data_root / "anomalib_format"

    labels_path = server_root / "dataset" / "labels.csv"
    labels_df = pd.read_csv(labels_path) if labels_path.exists() else None

    model = load_jina_model()
    warmup_model(model)

    image_dirs = [matwi_dir, anomalib_dir]
    images = find_all_images(image_dirs)
    logger.info("Total images to embed: %d", len(images))

    embeddings = generate_embeddings(model, images, labels_df=labels_df)
    write_embeddings_to_supabase(embeddings)

    output_path = data_root / "embeddings.json"
    import json

    serializable = []
    for emb in embeddings:
        serializable.append(
            {
                "image_name": emb["image_name"],
                "dim": emb["dim"],
                "set": emb.get("set"),
                "wear": emb.get("wear"),
            }
        )
    output_path.write_text(json.dumps(serializable, indent=2))
    logger.info("Embedding metadata saved to %s", output_path)


if __name__ == "__main__":
    main()
