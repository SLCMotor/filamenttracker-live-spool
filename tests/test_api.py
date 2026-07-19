from fastapi.testclient import TestClient

from app.main import app


def test_health_is_hardware_independent():
    with TestClient(app) as client:
        assert client.get("/settings").status_code == 200
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_mock_mode_exposes_mock_routes_but_not_system_controls():
    with TestClient(app) as client:
        assert client.post("/mock/weight", json={"weightGrams": 42}).status_code == 200
        assert client.post("/system/reboot").status_code == 404
