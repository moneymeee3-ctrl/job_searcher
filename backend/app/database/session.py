"""EMBEDHUNT AI — Async Session Factory"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database.engine import engine

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

async def get_db():
    from app.config.logging import get_logger
    logger = get_logger(__name__)
    async with AsyncSessionLocal() as session:
        try:
            yield session; await session.commit()
        except Exception as e:
            await session.rollback(); logger.error("db_session_error", error=str(e)); raise
        finally:
            await session.close()
