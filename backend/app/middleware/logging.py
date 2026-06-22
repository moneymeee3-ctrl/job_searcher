"""EMBEDHUNT AI — Request Logging Middleware"""
from fastapi import Request
from app.config.logging import get_logger
logger = get_logger("http")

async def logging_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info("http_request", method=request.method, path=request.url.path, status=response.status_code)
    return response
