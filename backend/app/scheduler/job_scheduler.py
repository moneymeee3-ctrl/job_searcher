"""EMBEDHUNT AI — Job pipeline scheduler.

Periodically runs the live job pipeline. The scheduler owns a session factory so
each run gets its own transaction. ``run_once`` is directly callable (used by
tests and manual triggers); ``start``/``stop`` manage the background interval
loop for production. All source failures are already isolated inside the
pipeline, so a run never crashes the loop.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.job_sources.base import Fetcher
from app.job_sources.pipeline import PipelineStats, run_pipeline

logger = logging.getLogger("embedhunt.scheduler")

SessionFactory = Callable[[], AsyncSession]


class JobPipelineScheduler:
    def __init__(self, session_factory: SessionFactory, *,
                 interval_seconds: float = 6 * 60 * 60,
                 fetcher: Fetcher | None = None):
        self.session_factory = session_factory
        self.interval_seconds = interval_seconds
        self.fetcher = fetcher
        self.run_count = 0
        self.last_run_at: Optional[datetime] = None
        self.last_stats: Optional[PipelineStats] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def run_once(self) -> PipelineStats:
        async with self.session_factory() as session:
            try:
                stats = await run_pipeline(session, fetcher=self.fetcher)
                await session.commit()
            except Exception:  # noqa: BLE001 — a bad run must not kill the loop
                await session.rollback()
                logger.exception("job pipeline run failed")
                stats = PipelineStats()
        self.run_count += 1
        self.last_run_at = datetime.now(timezone.utc)
        self.last_stats = stats
        return stats

    async def _loop(self) -> None:
        while self._running:
            await self.run_once()
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
