"""EMBEDHUNT AI — Startup tasks"""
from app.config.logging import get_logger
logger = get_logger(__name__)
async def run_startup_tasks() -> None:
    from app.database.dependency import check_db_connection
    logger.info("startup_tasks_begin")
    ok = await check_db_connection()
    logger.info("db_connection", status="ok" if ok else "failed")
