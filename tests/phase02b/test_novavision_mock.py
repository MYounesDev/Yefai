import base64
import os
from io import BytesIO

os.environ["NOVAVISION_MOCK"] = "true"

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from ai.novavision.config import NovaVisionSettings
from ai.novavision.inference import infer
from ai.novavision.schemas import InferenceRequest
from main import app

client = TestClient(app)


def test_novavision_health_mock_mode():
    response = client.get("/api/novavision/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] == "mock"
    assert data["container_running"] is True


def test_novavision_models_mock_mode():
    response = client.get("/api/novavision/models")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["mock"] is True


def test_novavision_deploy_mock_mode():
    response = client.post(
        "/api/novavision/deploy",
        json={"model_path": "artifacts/missing-model.pt", "app_name": "demo"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "mock"
    assert data["mock"] is True


def test_novavision_inference_base64_mock_mode():
    image_base64 = base64.b64encode(b"fake image bytes").decode("ascii")

    response = client.post(
        "/api/novavision/inference",
        json={"image_base64": image_base64, "model_id": "mock-model"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"]["mock"] is True
    assert data["result"]["anomaly_score"] >= 0

    job_response = client.get(f"/api/novavision/inference/{data['job_id']}")
    assert job_response.status_code == 200
    assert job_response.json()["job_id"] == data["job_id"]


def test_novavision_inference_requires_image_source():
    response = client.post("/api/novavision/inference", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_novavision_gateway_api_mode_uses_image_request_helper(monkeypatch):
    captured: dict[str, object] = {}

    def fake_send_image_to_novavision_json(image_path: str, **kwargs: object) -> tuple[int, dict]:
        captured["image_path"] = image_path
        with Image.open(image_path) as image:
            captured["image_size"] = image.size
        captured.update(kwargs)
        return 200, {
            "ulKkRn": {"status": "success"},
            "ZevSu2": {"status": "success"},
        }

    monkeypatch.setattr(
        "ai.novavision.inference.send_image_to_novavision_json",
        fake_send_image_to_novavision_json,
    )
    image_buffer = BytesIO()
    Image.new("RGB", (320, 180), color=(20, 80, 140)).save(image_buffer, format="JPEG")
    image_base64 = base64.b64encode(image_buffer.getvalue()).decode("ascii")
    settings = NovaVisionSettings(
        novavision_mock=False,
        novavision_inference_url="http://localhost:7001/api",
        novavision_app_port=3030,
    )

    result = await infer(
        InferenceRequest(image_base64=image_base64, model_id="19EC35"),
        settings=settings,
    )

    assert result.mock is False
    assert result.status == "completed"
    assert result.model_id == "19EC35"
    assert result.raw_response["node_statuses"] == {
        "ulKkRn": "success",
        "ZevSu2": "success",
    }
    assert captured["image_size"] == (256, 256)
    assert captured["api_url"] == "http://localhost:7001/api"
    assert captured["app_id"] == "19EC35"
    assert captured["port"] == 3030
