"""Health check router."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check() -> dict[str, str]:
    """Basic health check for the API."""
    return {"status": "ok", "service": "yefai-backend"}
