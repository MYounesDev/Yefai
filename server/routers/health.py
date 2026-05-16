"""Health check router."""

from ai.novavision.config import get_novavision_settings
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check() -> dict[str, str]:
    """Basic health check for the API."""
    novavision_settings = get_novavision_settings()
    return {
        "status": "ok",
        "version": "0.1.0",
        "supabase": "configured",
        "services": {
            "anomalib": "Phase 2A",
            "embeddings": "Phase 2A",
            "chat": "Phase 3A",
        },
        "novavision": {
            "mode": "mock" if novavision_settings.novavision_mock else "live",
            "inference_url": str(novavision_settings.novavision_inference_url),
        },
        "notifications": "Phase 3B",
        "spare_parts": "Phase 3B",
    }