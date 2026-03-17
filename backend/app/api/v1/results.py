"""Scraped results and export endpoints."""
import csv
import io
import json
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger(__name__)

from app.database import get_session
from app.models.scraped_item import ScrapedItem
from app.models.scrape_config import ScrapeConfig
from app.models.scrape_job import ScrapeJob
from app.repositories.item_repository import ItemRepository
from app.schemas.result import ScrapedItemResponse, ResultsListResponse, ResultStats

router = APIRouter()


@router.get("/", response_model=ResultsListResponse)
async def list_results(
    config_id: Optional[int] = Query(None),
    job_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """List scraped items with pagination and filtering."""
    repo = ItemRepository(session)
    offset = (page - 1) * page_size

    if job_id:
        items = await repo.get_by_job(job_id, offset=offset, limit=page_size)
        total = await repo.count_by_job(job_id)
    elif config_id:
        items = await repo.get_by_config(config_id, offset=offset, limit=page_size)
        total = await repo.count_by_config(config_id)
    else:
        items = await repo.get_all(offset=offset, limit=page_size)
        total = await repo.count()

    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return ResultsListResponse(
        items=[ScrapedItemResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/stats", response_model=ResultStats)
async def result_stats(
    session: AsyncSession = Depends(get_session),
):
    """Get aggregated statistics across all scraped data."""
    # Total items
    item_count_stmt = select(func.count()).select_from(ScrapedItem)
    total_items = (await session.execute(item_count_stmt)).scalar_one()

    # Total jobs
    job_count_stmt = select(func.count()).select_from(ScrapeJob)
    total_jobs = (await session.execute(job_count_stmt)).scalar_one()

    # Total configs
    config_count_stmt = select(func.count()).select_from(ScrapeConfig)
    total_configs = (await session.execute(config_count_stmt)).scalar_one()

    # Items by domain
    domain_stmt = (
        select(ScrapeConfig.domain, func.count(ScrapedItem.id))
        .join(ScrapeConfig, ScrapedItem.config_id == ScrapeConfig.id)
        .group_by(ScrapeConfig.domain)
    )
    domain_results = (await session.execute(domain_stmt)).all()
    items_by_domain = {row[0]: row[1] for row in domain_results}

    # Jobs by status
    status_stmt = (
        select(ScrapeJob.status, func.count(ScrapeJob.id))
        .group_by(ScrapeJob.status)
    )
    status_results = (await session.execute(status_stmt)).all()
    jobs_by_status = {row[0]: row[1] for row in status_results}

    return ResultStats(
        total_items=total_items,
        total_jobs=total_jobs,
        total_configs=total_configs,
        items_by_domain=items_by_domain,
        jobs_by_status=jobs_by_status,
    )


@router.get("/export")
async def export_results(
    format: str = Query("json", pattern="^(json|csv|xlsx)$"),
    config_id: Optional[int] = Query(None),
    job_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Export scraped results as JSON, CSV, or Excel (xlsx)."""
    repo = ItemRepository(session)

    if job_id:
        items = await repo.get_by_job(job_id, offset=0, limit=10000)
    elif config_id:
        items = await repo.get_by_config(config_id, offset=0, limit=10000)
    else:
        items = await repo.get_all(offset=0, limit=10000)

    if format == "csv":
        return _export_csv(items)
    elif format == "xlsx":
        return _export_excel(items)
    else:
        return _export_json(items)


@router.get("/{item_id}", response_model=ScrapedItemResponse)
async def get_result(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single scraped item by ID."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}")
async def delete_result(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a scraped item."""
    repo = ItemRepository(session)
    deleted = await repo.delete_by_id(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}


def _export_json(items) -> StreamingResponse:
    """Export items as JSON."""
    data = []
    for item in items:
        data.append({
            "id": item.id,
            "source_url": item.source_url,
            "item_url": item.item_url,
            "data": item.data,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })
    content = json.dumps(data, indent=2, ensure_ascii=False)
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=results.json"},
    )


def _export_excel(items) -> StreamingResponse:
    """Export items as Excel (xlsx) using openpyxl."""
    import openpyxl
    from openpyxl.styles import Font

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Results"

    headers_written = False

    for item in items:
        row_data = {
            "id": item.id,
            "source_url": item.source_url,
            "item_url": item.item_url,
            "created_at": item.created_at.isoformat() if item.created_at else "",
        }
        if isinstance(item.data, dict):
            for key, value in item.data.items():
                row_data[f"data_{key}"] = value

        if not headers_written:
            headers = list(row_data.keys())
            ws.append(headers)
            # Bold header row
            for cell in ws[1]:
                cell.font = Font(bold=True)
            headers_written = True

        ws.append(list(row_data.values()))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=results.xlsx"},
    )


def _export_csv(items) -> StreamingResponse:
    """Export items as CSV."""
    output = io.StringIO()
    writer = None

    for item in items:
        row = {
            "id": item.id,
            "source_url": item.source_url,
            "item_url": item.item_url,
            "created_at": item.created_at.isoformat() if item.created_at else "",
        }
        # Flatten the JSONB data field into individual columns
        if isinstance(item.data, dict):
            for key, value in item.data.items():
                row[f"data_{key}"] = value

        if writer is None:
            writer = csv.DictWriter(output, fieldnames=row.keys())
            writer.writeheader()

        writer.writerow(row)

    content = output.getvalue()
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"},
    )
