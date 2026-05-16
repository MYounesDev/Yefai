from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai.novavision.config import get_novavision_settings
from errors import YefaiError
from middleware.logging import RequestLoggingMiddleware
from middleware.org_context import OrgContextMiddleware
from routers import predictions
from routers.admin import router as admin_router
from routers.anomalib import router as anomalib_router
from routers.anomalies import router as anomalies_router
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.dashboard import router as dashboard_router
from routers.embeddings import router as embeddings_router
from routers.files import router as files_router
from routers.health import router as health_router
from routers.members import router as members_router
from routers.notifications import router as notifications_router
from routers.novavision import router as novavision_router
from routers.organizations import router as organizations_router
from routers.spare_parts import router as spare_parts_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Yefai API starting up...")
    yield
    # Shutdown
    logger.info("Yefai API shutting down...")

app = FastAPI(
    title="Yefai API",
    description="Predictive Maintenance Platform — Backend",
    version="0.2.0",
    lifespan=lifespan,
)

@app.exception_handler(YefaiError)
async def yefai_error_handler(request: Request, exc: YefaiError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "path": str(request.url.path)
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "tauri://localhost",
        "https://yefai.io",
        "https://app.yefai.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(OrgContextMiddleware)

# ── Existing routers (unchanged) ──────────────────────────────
app.include_router(anomalib_router)
app.include_router(embeddings_router)
app.include_router(novavision_router)
app.include_router(predictions.router)

app.include_router(health_router)

# ── New B2B SaaS routers (Phase B1–B8) ────────────────────────
app.include_router(auth_router)
app.include_router(organizations_router)
app.include_router(members_router)
app.include_router(admin_router)
app.include_router(files_router)
app.include_router(chat_router)
app.include_router(spare_parts_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(anomalies_router)
