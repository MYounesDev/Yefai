import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EmbeddingSearchRequest(BaseModel):
    query_text: str | None = None
    query_image_base64: str | None = None
    top_k: int = 10
    set_filter: int | None = None
    wear_min: float | None = None
    wear_max: float | None = None


class EmbeddingGenerateRequest(BaseModel):
    image_dir: str | None = None
    batch_size: int = 32


class EmbeddingService:
    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            script_dir = Path(__file__).resolve().parent
            server_root = script_dir.parent
            project_root = server_root.parent
        self._project_root = project_root
        self._model: Any = None
        self._model_loaded: bool = False

    def load_model(self) -> bool:
        try:
            from ai.embeddings.model import load_jina_model

            self._model = load_jina_model()
            self._model_loaded = True
            return True
        except Exception as e:
            logger.error("Failed to load Jina CLIP v2 model: %s", e)
            return False

    @property
    def model_loaded(self) -> bool:
        return self._model_loaded

    def search_by_text(self, query_text: str, top_k: int = 10, **filters) -> list[dict]:
        from ai.embeddings.search import text_search

        if not self._model_loaded and not self.load_model():
            raise RuntimeError("Embedding model not available")

        return text_search(query_text, top_k=top_k, model=self._model, **filters)

    def search_by_image(self, image_path: str, top_k: int = 10, **filters) -> list[dict]:
        from ai.embeddings.search import image_search

        if not self._model_loaded and not self.load_model():
            raise RuntimeError("Embedding model not available")

        return image_search(image_path, top_k=top_k, model=self._model, **filters)

    def get_image_embedding(self, image_id: str) -> dict[str, Any] | None:
        try:
            from db.client import get_supabase_client

            client = get_supabase_client()
            if client is None:
                return None

            response = client.table("images").select("*").eq("image_name", image_id).execute()
            if response.data:
                return response.data[0]  # type: ignore[return-value]
            return None
        except Exception as e:
            logger.error("Failed to fetch image embedding: %s", e)
            raise
