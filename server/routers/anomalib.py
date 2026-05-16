import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from services.anomalib_service import (
    AnomalibJobStatus,
    AnomalibModelInfo,
    AnomalibPredictRequest,
    AnomalibService,
    AnomalibTrainRequest,
)

router = APIRouter(prefix="/api/anomalib", tags=["anomalib"])

_train_jobs: dict[str, AnomalibJobStatus] = {}
_service = AnomalibService()


@router.post("/train", response_model=AnomalibJobStatus)
def train_anomalib(request: AnomalibTrainRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    _train_jobs[job_id] = AnomalibJobStatus(
        job_id=job_id, status="queued", progress=0.0, message="Training queued"
    )

    def _run_training():
        _train_jobs[job_id].status = "running"
        _train_jobs[job_id].message = "Training in progress"
        try:
            from pathlib import Path

            from ai.anomalib.train import train_patchcore

            dataset_path = (
                Path(request.dataset_path)
                if request.dataset_path
                else (_service._project_root / "data" / "anomalib_format")
            )
            models_dir = _service._project_root / "models"
            models_dir.mkdir(parents=True, exist_ok=True)
            train_patchcore(dataset_path, models_dir)

            _train_jobs[job_id].status = "completed"
            _train_jobs[job_id].progress = 1.0
            _train_jobs[job_id].message = "Training completed successfully"
        except Exception as e:
            _train_jobs[job_id].status = "failed"
            _train_jobs[job_id].message = str(e)

    background_tasks.add_task(_run_training)
    return _train_jobs[job_id]


@router.get("/status/{job_id}", response_model=AnomalibJobStatus)
def get_training_status(job_id: str):
    if job_id not in _train_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _train_jobs[job_id]


@router.post("/predict")
def predict_anomaly(request: AnomalibPredictRequest):
    if not _service.model_available:
        raise HTTPException(status_code=503, detail="Model not available. Train first.")
    try:
        result = _service.predict(request.image_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.get("/model/info", response_model=AnomalibModelInfo)
def get_model_info():
    return _service.get_model_info()
