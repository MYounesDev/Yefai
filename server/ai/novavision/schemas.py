from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ModelStatus(StrEnum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    MOCK = "mock"
    UNKNOWN = "unknown"


class DeployRequest(BaseModel):
    model_path: str
    app_name: str = "yefai-novavision"


class DeployedModel(BaseModel):
    app_id: str
    app_name: str
    model_path: str | None = None
    status: ModelStatus
    inference_url: str
    mock: bool = False


class HealthResponse(BaseModel):
    status: str
    mode: str
    inference_url: str
    container_running: bool
    active_app_id: str | None = None
    message: str


class InferenceRequest(BaseModel):
    image_path: str | None = None
    image_base64: str | None = None
    model_id: str | None = None

    @model_validator(mode="after")
    def require_image_source(self) -> "InferenceRequest":
        if not self.image_path and not self.image_base64:
            raise ValueError("image_path or image_base64 is required")
        return self


class InferenceResponse(BaseModel):
    job_id: str
    status: str
    result: "InferenceResult | None" = None


class InferenceResult(BaseModel):
    job_id: str
    status: str = "completed"
    anomaly_score: float = Field(ge=0.0)
    anomaly_map: list[list[float]] | None = None
    wear_type: str = "unknown"
    estimated_wear_um: float | None = None
    processing_time_ms: float
    model_id: str
    mock: bool = False
    source_image: str | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)


class PreprocessedImage(BaseModel):
    image_base64: str
    mime_type: str
    source_path: Path | None = None
    size_bytes: int
