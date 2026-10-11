from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DataSentry Unified Engine"


def test_api_profile_upload():
    with open("data/sample.csv", "rb") as f:
        response = client.post("/api/profile", files={"file": ("sample.csv", f, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "quality_score" in data
    assert data["summary"]["row_count"] == 20


def test_api_anomalies_upload():
    with open("data/sample.csv", "rb") as f:
        response = client.post("/api/anomalies", files={"file": ("sample.csv", f, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "IsolationForest"
    assert data["total_anomalies"] >= 1
