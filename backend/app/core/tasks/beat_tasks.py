"""Celery Beat periodic task — dispatches scrape jobs for due schedules."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog
from celery_app import celery

logger = structlog.get_logger()


def _run_async(coro):
    """Run an async coroutine from sync Celery task context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


async def _dispatch_due_schedules():
    """Find active schedules that are due and dispatch scrape jobs for them."""
    from croniter import croniter

    from app.core.tasks.scrape_task import execute_scrape_job
    from app.database import async_session_factory
    from app.models.scrape_job import ScrapeJob
    from app.models.scrape_schedule import ScrapeSchedule
    from sqlalchemy import select

    async with async_session_factory() as session:
        stmt = select(ScrapeSchedule).where(ScrapeSchedule.is_active == True)  # noqa: E712
        result = await session.execute(stmt)
        schedules = result.scalars().all()

        now = datetime.now(timezone.utc)
        dispatched = 0

        for schedule in schedules:
            try:
                cron = croniter(schedule.cron_expression, start_time=schedule.last_run_at or now)
                next_run = cron.get_next(datetime)

                # Update next_run_at
                schedule.next_run_at = next_run

                # Check if it's time to run (within a 1-minute window)
                if schedule.last_run_at is None or (now >= next_run):
                    job = ScrapeJob(config_id=schedule.config_id, status="pending")
                    session.add(job)
                    await session.flush()

                    execute_scrape_job.delay(job.id, schedule.config_id)

                    schedule.last_run_at = now
                    dispatched += 1

                    logger.info(
                        "schedule_dispatched",
                        schedule_id=schedule.id,
                        job_id=job.id,
                        config_id=schedule.config_id,
                    )
            except Exception as exc:
                logger.error(
                    "schedule_dispatch_error",
                    schedule_id=schedule.id,
                    error=str(exc),
                )

        await session.commit()
        return dispatched


@celery.task(name="schedules.dispatch_due")
def dispatch_due_schedules():
    """Celery Beat entry point: dispatch all due scheduled scrape jobs."""
    logger.info("beat_dispatch_due_schedules")
    dispatched = _run_async(_dispatch_due_schedules())
    logger.info("beat_dispatch_complete", dispatched=dispatched)
    return {"dispatched": dispatched}
