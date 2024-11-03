from fastapi.testclient import TestClient

from orchestrator.main import app


def client() -> TestClient:
    return TestClient(app)
