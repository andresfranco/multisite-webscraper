"""Prometheus-compatible metrics endpoint."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Response

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("")
async def get_metrics() -> Response:
    """Return basic Prometheus text metrics."""
    # TODO: Replace static counters with real application metrics.
    metrics_payload = """# HELP http_requests_total Total HTTP requests handled.
# TYPE http_requests_total counter
http_requests_total 0
# HELP scrape_jobs_total Total scrape jobs created.
# TYPE scrape_jobs_total counter
scrape_jobs_total 0
# HELP scrape_items_total Total scraped items processed.
# TYPE scrape_items_total counter
scrape_items_total 0
"""
    log.info("metrics_requested")
    return Response(content=metrics_payload, media_type="text/plain; version=0.0.4")
