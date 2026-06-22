"""EMBEDHUNT AI — Centralized Error Handler"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import EmbedHuntException
from app.config.logging import get_logger
from app.config.settings import settings
logger = get_logger(__name__)

async def embedhunt_exception_handler(request: Request, exc: EmbedHuntException):
    return JSONResponse(status_code=exc.status_code, content={"success":False,"error":exc.message})

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field":".".join(str(l) for l in e["loc"][1:]),"message":e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"success":False,"error":"Validation Error","details":errors})

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path, exc_info=True)
    msg = str(exc) if not settings.is_production else "Internal server error"
    return JSONResponse(status_code=500, content={"success":False,"error":msg})
