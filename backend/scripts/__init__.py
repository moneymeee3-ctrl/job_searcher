import asyncio

from app.database.engine import engine
from app.database.base import Base

# Import every model so SQLAlchemy knows about them.
import app.models  # noqa


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_db())