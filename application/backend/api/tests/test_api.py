from fastapi.testclient import TestClient
import uvicorn
from application.backend.api import app


client = TestClient(app)


def test_read_main():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"test": "works"}
