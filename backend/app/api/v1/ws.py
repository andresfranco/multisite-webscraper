"""FastAPI WebSocket endpoint for real-time job progress updates."""
from __future__ import annotations

import asyncio
import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger()

router = APIRouter()

# Channel prefix in Redis pub/sub
JOB_CHANNEL_PREFIX = "job_progress:"


@router.websocket("/jobs/{job_id}/progress")
async def job_progress_ws(websocket: WebSocket, job_id: int):
    """Stream real-time progress for a scrape job via WebSocket.

    The Celery worker publishes JSON updates to the Redis channel
    ``job_progress:{job_id}``.  This endpoint subscribes and forwards them to
    the connected client until the job reaches a terminal state or the client
    disconnects.
    """
    await websocket.accept()
    logger.info("ws_client_connected", job_id=job_id)

    try:
        import redis.asyncio as aioredis

        from app.config import get_settings

        settings = get_settings()
        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        pubsub = r.pubsub()
        channel = f"{JOB_CHANNEL_PREFIX}{job_id}"
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                data = json.loads(message["data"])
                await websocket.send_json(data)

                # Stop streaming once the job is in a terminal state
                if data.get("status") in ("completed", "failed", "cancelled"):
                    break

                # Allow cooperative multitasking
                await asyncio.sleep(0)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await r.aclose()

    except WebSocketDisconnect:
        logger.info("ws_client_disconnected", job_id=job_id)
    except Exception as exc:
        logger.error("ws_error", job_id=job_id, error=str(exc))
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
