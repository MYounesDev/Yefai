import base64

from fastapi.testclient import TestClient

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
