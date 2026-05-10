import pytest
from fastapi import HTTPException
from src.core.security.api_key import get_api_key
from src.core.config import settings

@pytest.mark.asyncio
async def test_get_api_key_valid():
    # settings.AI_SERVICE_API_KEY is the default for development
    valid_key = settings.AI_SERVICE_API_KEY
    result = await get_api_key(api_key_header=valid_key)
    assert result == valid_key

@pytest.mark.asyncio
async def test_get_api_key_invalid():
    invalid_key = "wrong_key"
    with pytest.raises(HTTPException) as excinfo:
        await get_api_key(api_key_header=invalid_key)
    
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Geçersiz veya eksik API Key."

@pytest.mark.asyncio
async def test_get_api_key_missing():
    with pytest.raises(HTTPException) as excinfo:
        await get_api_key(api_key_header=None)
    
    assert excinfo.value.status_code == 403
