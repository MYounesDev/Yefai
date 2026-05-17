
import pytest


class TestAnomalibRouter:
    def test_health_check(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert data["services"]["anomalib"] == "Phase 2A"

    def test_model_info_endpoint(self, test_client):
        response = test_client.get("/api/anomalib/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "backbone" in data
        assert "available" in data


class TestEmbeddingsRouter:
    def test_search_missing_query(self, test_client):
        response = test_client.post(
            "/api/embeddings/search",
            json={"top_k": 5},
        )
        data = response.json()
        assert "query_text or query_image_base64 required" in str(data["detail"])

    def test_image_embedding_not_found(self, test_client):
        response = test_client.get("/api/embeddings/image/nonexistent")
        assert response.status_code in (404, 500)


@pytest.fixture
def test_client():
    from fastapi.testclient import TestClient

    from main import app

    return TestClient(app)
