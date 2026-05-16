from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import predictions

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

# Include routers
app.include_router(predictions.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "supabase": "configured",
    }
