import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.recipe_sync_service import RecipeSyncService

@pytest.mark.asyncio
async def test_fetch_initial_recipes_success():
    service = RecipeSyncService()
    mock_recipes = [{"id": 1, "title": "Test Recipe"}]
    
    # We need to mock the client instance returned by the context manager
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_recipes
        mock_get.return_value = mock_response
        
        result = await service.fetch_initial_recipes()
        
        assert result == mock_recipes
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_initial_recipes_failure():
    service = RecipeSyncService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = await service.fetch_initial_recipes()
        
        assert result == []

@pytest.mark.asyncio
async def test_fetch_initial_recipes_exception():
    service = RecipeSyncService()
    
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection lost")):
        result = await service.fetch_initial_recipes()
        assert result == []
