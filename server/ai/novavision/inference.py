import time
from uuid import uuid4

import httpx

from ai.novavision.config import NovaVisionSettings, get_novavision_settings
from ai.novavision.preprocessing import preprocess_base64, preprocess_image
from ai.novavision.schemas import InferenceRequest, InferenceResult


async def infer(
    request: InferenceRequest, settings: NovaVisionSettings | None = None
) -> InferenceResult:
    settings = settings or get_novavision_settings()
    started = time.perf_counter()
    job_id = str(uuid4())
    model_id = request.model_id or settings.novavision_default_app_id

    preprocessed = (
        preprocess_image(request.image_path)
        if request.image_path
        else preprocess_base64(request.image_base64 or "")
    )

    if settings.novavision_mock:
        elapsed = (time.perf_counter() - started) * 1000
        return InferenceResult(
            job_id=job_id,
            anomaly_score=0.42,
            anomaly_map=[[0.0, 0.1], [0.2, 0.42]],
            wear_type="mock_wear",
            estimated_wear_um=42.0,
            processing_time_ms=elapsed,
            model_id=model_id,
            mock=True,
            source_image=str(preprocessed.source_path) if preprocessed.source_path else None,
            raw_response={"mode": "mock", "size_bytes": preprocessed.size_bytes},
        )

    payload = {
        "image": preprocessed.image_base64,
        "mime_type": preprocessed.mime_type,
        "model_id": model_id,
    }
    async with httpx.AsyncClient(timeout=settings.novavision_timeout_seconds) as client:
        response = await client.post(f"{settings.novavision_inference_url}/infer", json=payload)
    response.raise_for_status()
    data = response.json()
    elapsed = (time.perf_counter() - started) * 1000
    return InferenceResult(
        job_id=str(data.get("job_id") or job_id),
        status=str(data.get("status") or "completed"),
        anomaly_score=float(data.get("anomaly_score", 0.0)),
        anomaly_map=data.get("anomaly_map"),
        wear_type=str(data.get("wear_type") or "unknown"),
        estimated_wear_um=data.get("estimated_wear_um"),
        processing_time_ms=float(data.get("processing_time_ms") or elapsed),
        model_id=model_id,
        mock=False,
        source_image=str(preprocessed.source_path) if preprocessed.source_path else None,
        raw_response=data,
    )
