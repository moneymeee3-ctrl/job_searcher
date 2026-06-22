"""EMBEDHUNT AI — Structured Logging"""
import logging, sys, uuid
from contextvars import ContextVar
from typing import Optional
import structlog
from app.config.settings import settings

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def get_correlation_id() -> str: return _correlation_id.get() or str(uuid.uuid4())
def set_correlation_id(cid: Optional[str] = None) -> str:
    c = cid or str(uuid.uuid4()); _correlation_id.set(c); return c

def _add_correlation(logger, method, event_dict):
    event_dict["correlation_id"] = get_correlation_id(); return event_dict

def _add_context(logger, method, event_dict):
    event_dict["app"] = settings.APP_NAME; event_dict["env"] = settings.APP_ENV; return event_dict

def setup_logging() -> None:
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_correlation, _add_context,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    renderer = structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(colors=True)
    structlog.configure(
        processors=shared,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    fmt = structlog.stdlib.ProcessorFormatter(processors=[structlog.stdlib.ExtraAdder(), *shared[:-1], renderer])
    h = logging.StreamHandler(sys.stdout); h.setFormatter(fmt)
    root = logging.getLogger(); root.handlers.clear(); root.addHandler(h)
    root.setLevel(settings.LOG_LEVEL.upper())
    for n in ["uvicorn.access","sqlalchemy.engine"]: logging.getLogger(n).setLevel(logging.WARNING)

def get_logger(name: str): return structlog.get_logger(name)
