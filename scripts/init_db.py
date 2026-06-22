"""EMBEDHUNT AI — Create all database tables directly (dev / first-boot helper).

For production use Alembic migrations (`alembic upgrade head`). This script is a
fast path for local development and CI: it creates every ORM table against the
configured DATABASE_URL.

Run from the backend/ directory:
    python ../scripts/init_db.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make the backend package importable regardless of CWD.
BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.config.settings import settings  # noqa: E402
from app.database.base import Base  # noqa: E402
import app.models  # noqa: F401,E402 — registers all tables
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402


async def main() -> None:
    print(f"Connecting to: {settings.DATABASE_URL.split('@')[-1]}")
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    tables = ", ".join(sorted(Base.metadata.tables))
    print(f"Created {len(Base.metadata.tables)} tables: {tables}")


if __name__ == "__main__":
    asyncio.run(main())
