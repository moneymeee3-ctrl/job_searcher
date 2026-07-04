"""EMBEDHUNT AI — App Lifecycle (startup/shutdown)"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.logging import get_logger, setup_logging
from app.config.settings import settings
from sqlalchemy.ext.asyncio import AsyncEngine
from app.database.engine import engine
from app.database.base import Base

# VERY IMPORTANT
import app.models

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("embedhunt_starting", version=settings.APP_VERSION, env=settings.APP_ENV)
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

    logger.info("startup_tables_ok")
    from app.database.dependency import check_db_connection
    db_ok = await check_db_connection()
    if db_ok: logger.info("startup_db_ok")
    else: logger.error("startup_db_failed")
    logger.info("embedhunt_ready", port=settings.PORT)
    yield
    logger.info("embedhunt_shutdown")
