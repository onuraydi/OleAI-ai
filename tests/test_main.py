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
        "recipeId": "00000000-0000-0000-0000-000000000001",
        "title": "New Recipe",
        "ingredients": [{"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Test Ingredient", "amount": 1.0, "unit": "Adet", "aliases": []}],
        "category": "Test"
    }
    response = client.post("/api/v1/recipes/sync", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_lifespan_and_recommend():
    headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}
    payload = {
        "id": "00000000-0000-0000-0000-000000000000",
        "pantryItems": [{"id": "00000000-0000-0000-0000-000000000001", "name": "Tomato", "quantity": 2.0, "unit": "kg"}],
        "interactions": [],
        "mode": "default",
        "useZeroWaste": False
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/recommendations", json=payload, headers=headers)
        assert response.status_code == 200
        assert "recipes" in response.json()
