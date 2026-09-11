from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data


def test_health(client: TestClient):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Cloud Image API"


def test_database_health(client: TestClient):
    response = client.get("/api/v1/health/db")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"