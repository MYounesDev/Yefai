import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.novavision.config import get_novavision_settings
from routers import predictions
from routers.anomalib import router as anomalib_router
from routers.embeddings import router as embeddings_router
from routers.novavision import router as novavision_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yefai API",
    description="Predictive Maintenance Platform — Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anomalib_router)
app.include_router(embeddings_router)
app.include_router(novavision_router)
app.include_router(predictions.router)


@app.get("/health")
def health():
    novavision_settings = get_novavision_settings()
    return {
        "status": "ok",
        "version": "0.1.0",
        "supabase": "configured",
        "services": {
            "anomalib": "Phase 2A",
            "embeddings": "Phase 2A",
        },
        "novavision": {
            "mode": "mock" if novavision_settings.novavision_mock else "live",
            "inference_url": str(novavision_settings.novavision_inference_url),
        },
    }
