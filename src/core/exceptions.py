from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("OleAI-Exceptions")

class OleAIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, OleAIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    logger.error(f"Beklenmedik hata: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Sunucu tarafında beklenmedik bir hata oluştu."}
    )
