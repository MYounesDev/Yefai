import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SimilarImage(BaseModel):
    image_name: str
    set_name: str | None = None
    file_path: str | None = None
    wear_type: str | None = None
    wear: float | None = None
    flank_wear: float | None = None
    adhesive_wear: float | None = None
    combination_wear: float | None = None
    similarity: float
    rank: int


class SimilarImageRich(BaseModel):
    image_name: str
    similarity: float
    metadata: dict[str, Any] = Field(default_factory=dict)
    rank: int


class SearchResult(BaseModel):
    results: list[SimilarImage]
    count: int


class SearchResultRich(BaseModel):
    results: list[SimilarImageRich]
    count: int


class VectorSearchService:
    def search_similar(
        self,
        query_embedding: list[float],
        exclude_image_name: str | None = None,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> SearchResult:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            raise RuntimeError("Supabase client not available")

        try:
            resp = client.rpc(
                "search_similar_images",
                {
                    "query_embedding": query_embedding,
                    "exclude_image_name": exclude_image_name,
                    "top_k": top_k,
                    "min_similarity": min_similarity,
                },
            ).execute()

            results = [
                SimilarImage(
                    image_name=r["image_name"],
                    set_name=r.get("set_name"),
                    file_path=r.get("file_path"),
                    wear_type=r.get("wear_type"),
                    wear=r.get("wear"),
                    flank_wear=r.get("flank_wear"),
                    adhesive_wear=r.get("adhesive_wear"),
                    combination_wear=r.get("combination_wear"),
                    similarity=r["similarity"],
                    rank=r["rank"],
                )
                for r in (resp.data or [])
            ]
            return SearchResult(results=results, count=len(results))

        except Exception as e:
            logger.error("Vector search failed: %s", e)
            raise

    def search_similar_rich(
        self,
        query_embedding: list[float],
        exclude_image_name: str | None = None,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> SearchResultRich:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            raise RuntimeError("Supabase client not available")

        try:
            resp = client.rpc(
                "search_similar_images_rich",
                {
                    "query_embedding": query_embedding,
                    "exclude_image_name": exclude_image_name,
                    "top_k": top_k,
                    "min_similarity": min_similarity,
                },
            ).execute()

            results = [
                SimilarImageRich(
                    image_name=r["image_name"],
                    similarity=r["similarity"],
                    metadata=r.get("metadata", {}),
                    rank=r["rank"],
                )
                for r in (resp.data or [])
            ]
            return SearchResultRich(results=results, count=len(results))

        except Exception as e:
            logger.error("Rich vector search failed: %s", e)
            raise
