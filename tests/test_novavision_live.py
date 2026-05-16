import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.live
def test_novavision_live_health_requires_manual_gate():
    if os.getenv("NOVAVISION_MOCK", "true").lower() == "true":
        pytest.skip("NovaVision live mode is disabled; set NOVAVISION_MOCK=false for G2 live test")

    response = client.get("/api/novavision/health")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "live"
    assert data["container_running"] is True


@pytest.mark.live
def test_novavision_live_inference_with_phase2a_model():
    model_path = os.getenv("NOVAVISION_TEST_MODEL_PATH")
    image_path = os.getenv("NOVAVISION_TEST_IMAGE_PATH")
    if not model_path or not Path(model_path).exists():
        pytest.skip("NOVAVISION_TEST_MODEL_PATH must point to Phase 2A .pt artifact")
    if not image_path or not Path(image_path).exists():
        pytest.skip("NOVAVISION_TEST_IMAGE_PATH must point to a local test image")
    if os.getenv("NOVAVISION_MOCK", "true").lower() == "true":
        pytest.skip("NovaVision live mode is disabled; set NOVAVISION_MOCK=false for G2 live test")

    deploy = client.post(
        "/api/novavision/deploy",
        json={"model_path": model_path, "app_name": "phase2a-live-test"},
    )
    assert deploy.status_code == 200
    app_id = deploy.json()["app_id"]

    inference = client.post(
        "/api/novavision/inference",
        json={"image_path": image_path, "model_id": app_id},
    )
    assert inference.status_code == 200
    result = inference.json()["result"]
    assert result["mock"] is False
    assert result["anomaly_score"] >= 0
