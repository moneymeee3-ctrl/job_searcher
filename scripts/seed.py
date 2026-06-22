"""EMBEDHUNT AI — Seed reference data (companies) into the database.

Idempotent: skips companies that already exist (by name). Safe to re-run.

Run from the backend/ directory:
    python ../scripts/seed.py
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.config.settings import settings  # noqa: E402
from app.models.company import Company  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

# (name, tier, careers_url)
COMPANIES = [
    ("Qualcomm", "tier1_semiconductor", "https://careers.qualcomm.com"),
    ("NVIDIA", "tier1_semiconductor", "https://nvidia.com/careers"),
    ("NXP Semiconductors", "tier1_semiconductor", "https://careers.nxp.com"),
    ("Texas Instruments", "tier1_semiconductor", "https://careers.ti.com"),
    ("Infineon Technologies", "tier1_semiconductor", "https://infineon.com/careers"),
    ("AMD", "tier1_semiconductor", "https://jobs.amd.com"),
    ("STMicroelectronics", "tier1_semiconductor", "https://st.com/careers"),
    ("Bosch Global Software Technologies", "tier2_automotive", "https://bosch.com/careers"),
    ("KPIT Technologies", "tier2_automotive", "https://kpit.com/careers"),
    ("Continental", "tier2_automotive", "https://continental.com/careers"),
    ("Aptiv", "tier2_automotive", "https://aptiv.com/careers"),
    ("Harman International", "tier2_automotive", "https://harman.com/careers"),
    ("Tata Elxsi", "india_focused", "https://tataelxsi.com/careers"),
    ("L&T Technology Services", "india_focused", "https://ltts.com/careers"),
    ("Cisco Systems", "tier4_telecom", "https://jobs.cisco.com"),
    ("Siemens", "tier3_industrial", "https://jobs.siemens.com"),
]


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    created = 0
    async with Session() as session:
        for name, tier, url in COMPANIES:
            exists = await session.scalar(select(Company).where(Company.name == name))
            if exists:
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            session.add(Company(name=name, slug=slug, tier=tier, careers_url=url))
            created += 1
        await session.commit()
    await engine.dispose()
    print(f"Seed complete. Added {created} new companies ({len(COMPANIES)} total in catalog).")


if __name__ == "__main__":
    asyncio.run(main())
