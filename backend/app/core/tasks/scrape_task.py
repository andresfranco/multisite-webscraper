"""Celery tasks for scraping operations."""
import asyncio
import json
from datetime import datetime, timezone

import structlog
from celery_app import celery

logger = structlog.get_logger()

# Redis pub/sub channel prefix (must match ws.py)
JOB_CHANNEL_PREFIX = "job_progress:"


def _run_async(coro):
    """Run an async coroutine from sync Celery task context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, create a new one
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


async def _publish_progress(redis_client, job_id: int, data: dict) -> None:
    """Publish a progress update to the Redis pub/sub channel for a job."""
    try:
        channel = f"{JOB_CHANNEL_PREFIX}{job_id}"
        await redis_client.publish(channel, json.dumps(data))
    except Exception as exc:
        logger.debug("redis_publish_failed", job_id=job_id, error=str(exc))


async def _execute_scrape(job_id: int, config_id: int, task_instance=None):
    """Async implementation of the scrape job execution."""
    from app.core.scraping.engine import ScrapingEngine
    from app.database import async_session_factory
    from app.models.job_log import JobLog
    from app.models.scrape_config import ScrapeConfig
    from app.models.scrape_job import ScrapeJob
    from app.models.scraped_item import ScrapedItem
    from app.config import get_settings
    import redis.asyncio as aioredis

    settings = get_settings()
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

    async with async_session_factory() as session:
        try:
            # Load config
            config = await session.get(ScrapeConfig, config_id)
            if config is None:
                logger.error("config_not_found", config_id=config_id)
                return {"job_id": job_id, "status": "failed", "error": "Config not found"}

            # Update job status to running
            job = await session.get(ScrapeJob, job_id)
            if job is None:
                logger.error("job_not_found", job_id=job_id)
                return {"job_id": job_id, "status": "failed", "error": "Job not found"}

            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            await session.commit()

            # Log start
            log_entry = JobLog(
                job_id=job_id,
                level="INFO",
                message=f"Starting scrape job for config '{config.name}' ({config.base_url})",
            )
            session.add(log_entry)
            await session.commit()

            # Build config dict for the engine
            config_dict = {
                "base_url": config.base_url,
                "item_selector": config.item_selector,
                "fields": config.fields if isinstance(config.fields, list) else [],
                "pagination_type": config.pagination_type,
                "pagination_selector": config.pagination_selector,
                "max_pages": config.max_pages,
                "request_delay_ms": config.request_delay_ms,
                "custom_headers": config.custom_headers,
                "use_headless_browser": config.use_headless_browser,
                "wait_for_selector": config.wait_for_selector,
            }

            # Run the scraping engine
            engine = ScrapingEngine(config_dict)

            async def progress_callback(progress):
                """Update job progress in the database and publish to Redis."""
                job.pages_scraped = progress.get("pages_scraped", 0)
                job.items_found = progress.get("items_found", 0)
                await session.commit()

                # Publish to Redis pub/sub for WebSocket clients
                await _publish_progress(redis_client, job_id, {
                    "job_id": job_id,
                    "status": "running",
                    "pages_scraped": progress.get("pages_scraped", 0),
                    "pages_total": progress.get("pages_total", 1),
                    "items_found": progress.get("items_found", 0),
                    "current_url": progress.get("current_url", ""),
                })

                # Update Celery task state
                if task_instance:
                    task_instance.update_state(
                        state="PROGRESS",
                        meta={
                            "job_id": job_id,
                            "pages_scraped": progress.get("pages_scraped", 0),
                            "pages_total": progress.get("pages_total", 1),
                            "items_found": progress.get("items_found", 0),
                            "current_url": progress.get("current_url", ""),
                        },
                    )

            result = await engine.run(progress_callback=progress_callback)

            # Store scraped items
            items_created = 0
            items_skipped = 0

            for item_data in result["items"]:
                content_hash = item_data.get("content_hash")

                # Check for duplicate
                if content_hash:
                    from sqlalchemy import select

                    existing_stmt = select(ScrapedItem).where(
                        ScrapedItem.content_hash == content_hash
                    )
                    existing_result = await session.execute(existing_stmt)
                    if existing_result.scalar_one_or_none():
                        items_skipped += 1
                        continue

                scraped_item = ScrapedItem(
                    job_id=job_id,
                    config_id=config_id,
                    source_url=item_data["source_url"],
                    item_url=item_data.get("item_url"),
                    data=item_data["data"],
                    content_hash=content_hash,
                )
                session.add(scraped_item)
                items_created += 1

            await session.commit()

            # Publish completion to Redis
            await _publish_progress(redis_client, job_id, {
                "job_id": job_id,
                "status": "completed",
                "pages_scraped": result["pages_scraped"],
                "items_found": result["items_found"],
                "items_created": items_created,
                "items_skipped": items_skipped,
                "errors": result["errors"],
            })

            # Update job as completed
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            job.pages_scraped = result["pages_scraped"]
            job.items_found = result["items_found"]
            job.items_created = items_created
            job.items_skipped = items_skipped
            job.errors = result["errors"]

            # Log completion
            completion_log = JobLog(
                job_id=job_id,
                level="INFO",
                message=(
                    f"Job completed: {result['pages_scraped']} pages scraped, "
                    f"{items_created} items created, {items_skipped} skipped, "
                    f"{result['errors']} errors"
                ),
            )
            session.add(completion_log)
            await session.commit()

            logger.info(
                "scrape_job_completed",
                job_id=job_id,
                pages=result["pages_scraped"],
                items_created=items_created,
                items_skipped=items_skipped,
            )

            return {
                "job_id": job_id,
                "status": "completed",
                "pages_scraped": result["pages_scraped"],
                "items_created": items_created,
                "items_skipped": items_skipped,
                "errors": result["errors"],
            }

        except Exception as e:
            logger.error("scrape_job_failed", job_id=job_id, error=str(e))

            # Publish failure to Redis
            await _publish_progress(redis_client, job_id, {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
            })

            # Update job as failed
            try:
                job = await session.get(ScrapeJob, job_id)
                if job:
                    job.status = "failed"
                    job.completed_at = datetime.now(timezone.utc)
                    job.error_message = str(e)

                    error_log = JobLog(
                        job_id=job_id,
                        level="ERROR",
                        message=f"Job failed: {e}",
                    )
                    session.add(error_log)
                    await session.commit()
            except Exception:
                pass

            return {"job_id": job_id, "status": "failed", "error": str(e)}

        finally:
            await redis_client.aclose()


@celery.task(
    bind=True,
    name="scrape.execute",
    max_retries=3,
    default_retry_delay=60,  # base seconds; exponential backoff applied below
)
def execute_scrape_job(self, job_id: int, config_id: int):
    """Execute a scrape job (Celery task entry point).

    Retries up to 3 times with exponential backoff (60s, 120s, 240s) on
    transient failures.  Permanent failures (e.g. config not found) are not
    retried and mark the job as failed immediately.
    """
    logger.info("celery_task_started", job_id=job_id, config_id=config_id, attempt=self.request.retries)
    try:
        return _run_async(_execute_scrape(job_id, config_id, task_instance=self))
    except Exception as exc:
        retry_count = self.request.retries
        if retry_count < self.max_retries:
            backoff = 60 * (2 ** retry_count)  # 60, 120, 240 seconds
            logger.warning(
                "celery_task_retry",
                job_id=job_id,
                attempt=retry_count + 1,
                backoff_seconds=backoff,
                error=str(exc),
            )
            raise self.retry(exc=exc, countdown=backoff)
        logger.error("celery_task_exhausted_retries", job_id=job_id, error=str(exc))
        raise
