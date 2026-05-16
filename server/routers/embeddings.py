from fastapi import APIRouter, HTTPException

from services.embedding_service import (
    EmbeddingSearchRequest,
    EmbeddingService,
)

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])

_service = EmbeddingService()


@router.post("/search")
def search_embeddings(request: EmbeddingSearchRequest):
    if not _service.model_loaded:
        try:
            _service.load_model()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Model not available: {e}") from e

    try:
        filters: dict[str, object] = {}
        if request.set_filter is not None:
            filters["set"] = request.set_filter
        if request.wear_min is not None:
            filters["wear_min"] = request.wear_min
        if request.wear_max is not None:
            filters["wear_max"] = request.wear_max

        if request.query_text:
            results = _service.search_by_text(request.query_text, request.top_k, **filters)
        elif request.query_image_base64:
            import base64
            import tempfile
            from pathlib import Path

            img_data = base64.b64decode(request.query_image_base64)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(img_data)
                temp_path = f.name
            try:
                results = _service.search_by_image(temp_path, request.top_k, **filters)
            finally:
                Path(temp_path).unlink(missing_ok=True)
        else:
            raise HTTPException(status_code=400, detail="query_text or query_image_base64 required")

        return {"results": results, "count": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
