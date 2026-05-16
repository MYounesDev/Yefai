from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.novavision.config import get_novavision_settings
from routers.novavision import router as novavision_router

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

app.include_router(novavision_router)


@app.get("/health")
def health():
    novavision_settings = get_novavision_settings()
    return {
        "status": "ok",
        "version": "0.1.0",
        "supabase": "configured",
        "novavision": {
            "mode": "mock" if novavision_settings.novavision_mock else "live",
            "inference_url": str(novavision_settings.novavision_inference_url),
        },
    }
