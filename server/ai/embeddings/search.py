import logging
from typing import Any

import numpy as np

from ai.embeddings.model import encode_text, get_device, load_jina_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def search_similar_images(
    query_vector: list[float],
    top_k: int = 10,
    org_id: str | None = None,
    set_filter: int | None = None,
    wear_min: float | None = None,
    wear_max: float | None = None,
) -> list[dict[str, Any]]:
    try:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            logger.warning("Supabase client not available")
            return []

        rpc_params = {
            "query_embedding": query_vector,
            "match_count": top_k,
        }
        response = client.rpc("match_images", rpc_params).execute()
        results: list[dict[str, Any]] = list(response.data) if response.data else []  # type: ignore[arg-type]

        if org_id is not None:
            results = [r for r in results if r.get("org_id") == org_id]
        if set_filter is not None:
            results = [r for r in results if r.get("set") == set_filter]
        if wear_min is not None:
            results = [r for r in results if r.get("wear", 0) >= wear_min]
        if wear_max is not None:
            results = [r for r in results if r.get("wear", float("inf")) <= wear_max]

        for r in results:
            r["similarity"] = cosine_similarity(query_vector, r.get("image_embedding", []))

        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return results[:top_k]

    except ImportError:
        logger.warning("Supabase SDK not available")
        return []
    except Exception as e:
        logger.error("Search failed: %s", e)
        return []


def text_search(
    query_text: str,
    top_k: int = 10,
    model: Any = None,
    **metadata_filters,
) -> list[dict[str, Any]]:
    if model is None:
        model = load_jina_model()

    device = get_device()
    query_vector = encode_text(model, query_text, device)

    return search_similar_images(
        query_vector,
        top_k=top_k,
        org_id=metadata_filters.get("org_id"),
        set_filter=metadata_filters.get("set"),
        wear_min=metadata_filters.get("wear_min"),
        wear_max=metadata_filters.get("wear_max"),
    )


def image_search(
    image_path: str,
    top_k: int = 10,
    model: Any = None,
    **metadata_filters,
) -> list[dict[str, Any]]:
    from PIL import Image

    from ai.embeddings.model import encode_image

    if model is None:
        model = load_jina_model()

    device = get_device()
    image = Image.open(image_path).convert("RGB")
    query_vector = encode_image(model, image, device)

    return search_similar_images(
        query_vector,
        top_k=top_k,
        org_id=metadata_filters.get("org_id"),
        set_filter=metadata_filters.get("set"),
        wear_min=metadata_filters.get("wear_min"),
        wear_max=metadata_filters.get("wear_max"),
    )
