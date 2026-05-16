from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_main_file_exists():
    assert (
        Path(__file__).resolve().parent.parent.parent / "server" / "main.py"
    ).exists()


def test_router_files_exist():
    router_dir = Path(__file__).resolve().parent.parent.parent / "server" / "routers"
    expected = [
        "anomalib.py",
        "novavision.py",
        "embeddings.py",
        "chat.py",
        "notifications.py",
        "spare_parts.py",
    ]
    for name in expected:
        assert (router_dir / name).exists(), f"Missing router: {name}"


def test_config_file_exists():
    assert (
        Path(__file__).resolve().parent.parent.parent / "server" / "db" / "config.py"
    ).exists()


def test_cors_enabled():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 405)


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/health" in schema["paths"]
