"""EMBEDHUNT AI — Correlation ID Middleware"""
import uuid
from fastapi import Request, Response
from app.config.logging import set_correlation_id

async def correlation_middleware(request: Request, call_next):
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    set_correlation_id(cid)
    import time; t0 = time.perf_counter()
    response: Response = await call_next(request)
    ms = round((time.perf_counter()-t0)*1000, 2)
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Response-Time"] = f"{ms}ms"
    return response
