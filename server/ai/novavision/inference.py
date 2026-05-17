import asyncio
import base64
import logging
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx

from ai.novavision.config import NovaVisionSettings, get_novavision_settings
from ai.novavision.image_request import resize_image_to_256, send_image_to_novavision_json
from ai.novavision.preprocessing import preprocess_base64, preprocess_image
from ai.novavision.schemas import InferenceRequest, InferenceResult

logger = logging.getLogger(__name__)


def _temporary_image_path(image_base64: str, mime_type: str) -> Path:
    suffix = ".png" if mime_type == "image/png" else ".jpg"
    decoded = base64.b64decode(image_base64)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        temp_file.write(decoded)
        return Path(temp_file.name)


async def _infer_via_novavision_gateway(
    *,
    preprocessed_image_base64: str,
    preprocessed_mime_type: str,
    source_image_path: str | None,
    settings: NovaVisionSettings,
    model_id: str,
) -> tuple[int, object]:
    image_path = (
        Path(source_image_path)
        if source_image_path
        else _temporary_image_path(preprocessed_image_base64, preprocessed_mime_type)
    )
    with tempfile.NamedTemporaryFile(
        suffix=image_path.suffix or ".jpg", delete=False
    ) as resized_file:
        resized_path = Path(resized_file.name)
    try:
        resized_image_path = await asyncio.to_thread(
            resize_image_to_256,
            str(image_path),
            str(resized_path),
        )
        return await asyncio.to_thread(
            send_image_to_novavision_json,
            resized_image_path,
            api_url=settings.novavision_inference_url,
            app_id=model_id,
            port=settings.novavision_app_port,
            timeout=int(settings.novavision_timeout_seconds),
        )
    finally:
        if source_image_path is None:
            image_path.unlink(missing_ok=True)
        resized_path.unlink(missing_ok=True)


def _extract_node_output(node_data: dict, output_name: str = "outputImage") -> str | None:
    try:
        return node_data["configs"]["executor"]["value"]["value"]["outputs"][output_name]["value"][
            "value"
        ]
    except (KeyError, TypeError):
        return None


def _save_base64_image(image_base64: str, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or Path(tempfile.gettempdir()) / "novavision_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"normalized_{uuid4().hex[:8]}.jpg"
    image_bytes = base64.b64decode(image_base64)
    output_path.write_bytes(image_bytes)
    return output_path


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

    if str(settings.novavision_inference_url).rstrip("/").endswith("/api"):
        status_code, data = await _infer_via_novavision_gateway(
            preprocessed_image_base64=preprocessed.image_base64,
            preprocessed_mime_type=preprocessed.mime_type,
            source_image_path=str(preprocessed.source_path) if preprocessed.source_path else None,
            settings=settings,
            model_id=model_id,
        )
        if status_code != 200 or not isinstance(data, dict):
            raise ValueError(f"NovaVision gateway request failed with HTTP {status_code}")
        node_statuses = {
            key: value.get("status")
            for key, value in data.items()
            if isinstance(value, dict) and "status" in value
        }
        failed_nodes = {
            key: node_status
            for key, node_status in node_statuses.items()
            if node_status != "success"
        }
        if failed_nodes:
            raise ValueError(f"NovaVision gateway node failure: {failed_nodes}")
        elapsed = (time.perf_counter() - started) * 1000

        normalized_image_base64 = None
        normalized_image_path = None
        for node_key in data:
            if isinstance(data[node_key], dict):
                extracted = _extract_node_output(data[node_key], "outputImage")
                if extracted:
                    normalized_image_base64 = extracted
                    try:
                        normalized_image_path = str(_save_base64_image(extracted))
                    except Exception as exc:
                        logger.warning("Failed to save normalized image: %s", exc)

        return InferenceResult(
            job_id=job_id,
            status="completed",
            anomaly_score=0.0,
            anomaly_map=None,
            wear_type="preprocessed",
            estimated_wear_um=None,
            processing_time_ms=elapsed,
            model_id=model_id,
            mock=False,
            source_image=str(preprocessed.source_path) if preprocessed.source_path else None,
            raw_response={
                "node_statuses": node_statuses,
                "gateway_response": data,
                "normalized_image_path": normalized_image_path,
                "normalized_image_base64_preview": normalized_image_base64[:80] + "..."
                if normalized_image_base64
                else None,
            },
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
