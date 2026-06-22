"""EMBEDHUNT AI — Prometheus metrics.

A small, dependency-light metrics layer built directly on ``prometheus_client``.
We deliberately avoid third-party FastAPI instrumentators here: their route
introspection breaks on mounted/included routers in current FastAPI versions.
This middleware records request count and latency by method, templated path and
status, and exposes them at ``/metrics``.
"""
from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "embedhunt_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "embedhunt_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


def _template_path(request: Request) -> str:
    """Use the matched route template (e.g. /jobs/{id}) to keep label cardinality low."""
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path or request.url.path


def setup_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def _metrics_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        path = _template_path(request)
        if path != "/metrics":
            REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
            REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
