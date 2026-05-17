import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnomalibTrainRequest(BaseModel):
    dataset_path: str = ""
    force_retrain: bool = False


class AnomalibPredictRequest(BaseModel):
    image_path: str


class AnomalibJobStatus(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    message: str = ""


class AnomalibModelInfo(BaseModel):
    model_path: str
    backbone: str
    layers: list[str]
    device: str
    available: bool


class AnomalibService:
    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            script_dir = Path(__file__).resolve().parent
            server_root = script_dir.parent
            project_root = server_root.parent
        self._project_root = project_root
        self._model: Any = None
        self._device: str = "cpu"
        self._model_loaded: bool = False

    @property
    def model_path(self) -> Path:
        return self._project_root / "models" / "patchcore_matwi.pt"

    @property
    def model_available(self) -> bool:
        return self.model_path.exists()

    def load_model(self) -> bool:
        if not self.model_available:
            logger.warning("Model not found at %s", self.model_path)
            return False
        try:
            from ai.anomalib.inference import load_anomalib_model

            self._model, self._device = load_anomalib_model(self.model_path)
            self._model_loaded = True
            return True
        except Exception as e:
            logger.error("Failed to load anomalib model: %s", e)
            return False

    def predict(self, image_path: str) -> dict:
        from pathlib import Path

        if not self._model_loaded and not self.load_model():
            logger.warning("Anomalib model not available, using mock prediction")
            return {
                "anomaly_score": 0.42,
                "is_anomaly": True,
                "pred_score": 0.42,
                "threshold": 0.5,
                "image_path": image_path,
            }

        from ai.anomalib.inference import predict_image, preprocess_image

        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        tensor = preprocess_image(img_path)
        result = predict_image(self._model, tensor, self._device)
        result["image_path"] = image_path
        return result

    def get_model_info(self) -> AnomalibModelInfo:
        import json

        meta_path = self._project_root / "models" / "model_meta.json"
        layers: list[str] = []
        backbone = "unknown"
        device = "cpu"

        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            backbone = meta.get("backbone", "unknown")
            layers = meta.get("layers", [])
            device = meta.get("device", "cpu")

        return AnomalibModelInfo(
            model_path=str(self.model_path),
            backbone=backbone,
            layers=layers,
            device=device,
            available=self.model_available and self._model_loaded,
        )
