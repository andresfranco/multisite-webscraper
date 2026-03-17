"""Scrape configuration CRUD endpoints."""
from typing import Sequence
from urllib.parse import urlparse

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger(__name__)

from app.core.scraping.auto_detect import AutoDetector
from app.core.scraping.engine import ScrapingEngine
from app.core.scraping.fetcher import fetch_page
from app.database import get_session
from app.models.scrape_config import ScrapeConfig
from app.repositories.config_repository import ConfigRepository
from app.schemas.auto_detect import AutoDetectRequest, AutoDetectResponse
from app.schemas.config import (
    ScrapeConfigCreate,
    ScrapeConfigUpdate,
    ScrapeConfigResponse,
)
from app.utils.url_utils import is_safe_url

router = APIRouter()


@router.post("/auto-detect", response_model=AutoDetectResponse)
async def auto_detect_config(request: AutoDetectRequest):
    """Auto-detect a scrape config from a URL."""
    url = str(request.url)
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="URL is not allowed")

    html = await fetch_page(url=url, use_playwright=request.use_playwright)
    if html is None:
        raise HTTPException(status_code=502, detail="Failed to fetch page")

    detector = AutoDetector(url=url, html=html)
    result = detector.detect()
    return AutoDetectResponse(**result)


@router.get("/", response_model=list[ScrapeConfigResponse])
async def list_configs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    """List all scrape configurations."""
    repo = ConfigRepository(session)
    configs = await repo.get_all(offset=offset, limit=limit)
    return configs


@router.post("/", response_model=ScrapeConfigResponse, status_code=201)
async def create_config(
    config_in: ScrapeConfigCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new scrape configuration."""
    repo = ConfigRepository(session)

    # Build the ORM object
    domain = urlparse(config_in.base_url).netloc
    db_config = ScrapeConfig(
        name=config_in.name,
        base_url=config_in.base_url,
        domain=domain,
        use_headless_browser=config_in.use_headless_browser,
        wait_for_selector=config_in.wait_for_selector,
        custom_headers=config_in.custom_headers,
        pagination_type=config_in.pagination_type,
        pagination_selector=config_in.pagination_selector,
        max_pages=config_in.max_pages,
        item_selector=config_in.item_selector,
        fields=[f.model_dump() for f in config_in.fields],
        request_delay_ms=config_in.request_delay_ms,
        concurrent_requests=config_in.concurrent_requests,
        schedule_cron=config_in.schedule_cron,
        is_active=config_in.is_active,
    )
    created = await repo.create(db_config)
    return created


@router.get("/{config_id}", response_model=ScrapeConfigResponse)
async def get_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single scrape configuration by ID."""
    repo = ConfigRepository(session)
    config = await repo.get_by_id(config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.put("/{config_id}", response_model=ScrapeConfigResponse)
async def update_config(
    config_id: int,
    config_in: ScrapeConfigUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing scrape configuration."""
    repo = ConfigRepository(session)
    config = await repo.get_by_id(config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")

    update_data = config_in.model_dump(exclude_unset=True)

    # Recalculate domain if base_url changed
    if "base_url" in update_data:
        update_data["domain"] = urlparse(update_data["base_url"]).netloc

    # Serialize fields if provided
    if "fields" in update_data and update_data["fields"] is not None:
        update_data["fields"] = [
            f.model_dump() if hasattr(f, "model_dump") else f
            for f in update_data["fields"]
        ]

    updated = await repo.update(config, update_data)
    return updated


@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a scrape configuration."""
    repo = ConfigRepository(session)
    deleted = await repo.delete_by_id(config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"message": "Config deleted"}


@router.post("/{config_id}/test")
async def test_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Test a saved config against one page without persisting results."""
    stmt = select(ScrapeConfig).where(ScrapeConfig.id == config_id)
    result = await session.execute(stmt)
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")

    engine_config = {
        "base_url": config.base_url,
        "item_selector": config.item_selector,
        "fields": config.fields if isinstance(config.fields, list) else [],
        "pagination_type": config.pagination_type,
        "pagination_selector": config.pagination_selector,
        "max_pages": 1,
        "request_delay_ms": config.request_delay_ms,
        "custom_headers": config.custom_headers,
        "use_headless_browser": config.use_headless_browser,
        "wait_for_selector": config.wait_for_selector,
    }

    scrape_result = await ScrapingEngine(engine_config).run()
    return {
        "items": [item["data"] for item in scrape_result["items"]],
        "pages_scraped": scrape_result["pages_scraped"],
        "items_found": scrape_result["items_found"],
        "errors": scrape_result["errors"],
    }
