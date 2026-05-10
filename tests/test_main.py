from fastapi.testclient import TestClient
from src.main import app
from src.core.config import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_recommendations_unauthorized():
    response = client.post("/api/v1/recommendations", json={})
    assert response.status_code == 403 # Missing API Key

def test_recommendations_authorized_empty_payload():
    headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}
    # Empty payload should fail validation (Pydantic)
    response = client.post("/api/v1/recommendations", json={}, headers=headers)
    assert response.status_code == 422

def test_sync_recipe_authorized():
    headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}
    payload = {
        "recipe_id": "00000000-0000-0000-0000-000000000001",
        "title": "New Recipe",
        "ingredients": "test ingredients",
        "category": "Test"
    }
    response = client.post("/api/v1/recipes/sync", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
