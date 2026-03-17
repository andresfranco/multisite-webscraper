"""Health and readiness endpoints for monitoring."""
from __future__ import annotations

from datetime import datetime, timezone

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session

log = structlog.get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.get("")
async def health_check() -> dict[str, str]:
    """Return basic service health information."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log.info("health_check_requested", timestamp=timestamp)
    return {"status": "healthy", "timestamp": timestamp, "version": "1.0.0"}


@router.get("/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    """Verify database and Redis connectivity."""
    checks = {"database": "error", "redis": "error"}
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"

        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        log.exception("readiness_check_failed", checks=checks, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks},
        )
    finally:
        await redis_client.aclose()

    log.info("readiness_check_succeeded", checks=checks)
    return {"status": "ready", "checks": checks}
