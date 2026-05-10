import pytest
from fastapi import Request
from src.core.exceptions import OleAIException, global_exception_handler

class MockRequest:
    pass

@pytest.mark.asyncio
async def test_oleai_exception_handler():
    request = MockRequest()
    exc = OleAIException(message="Custom error", status_code=418)
    
    response = await global_exception_handler(request, exc)
    
    assert response.status_code == 418
    import json
    content = json.loads(response.body)
    assert content["detail"] == "Custom error"

@pytest.mark.asyncio
async def test_unexpected_exception_handler():
    request = MockRequest()
    exc = ValueError("Unexpected crash")
    
    response = await global_exception_handler(request, exc)
    
    assert response.status_code == 500
    import json
    content = json.loads(response.body)
    assert content["detail"] == "Sunucu tarafında beklenmedik bir hata oluştu."
