"""Pydantic schemas for API request/response validation."""

from app.schemas.common import MessageResponse, PaginationParams
from app.schemas.config import (
    FieldConfigSchema,
    ScrapeConfigCreate,
    ScrapeConfigResponse,
    ScrapeConfigUpdate,
)
from app.schemas.job import JobCreate, JobProgress, JobResponse
from app.schemas.result import ResultStats, ResultsListResponse, ScrapedItemResponse

__all__ = [
    "FieldConfigSchema",
    "ScrapeConfigCreate",
    "ScrapeConfigUpdate",
    "ScrapeConfigResponse",
    "JobCreate",
    "JobResponse",
    "JobProgress",
    "ScrapedItemResponse",
    "ResultsListResponse",
    "ResultStats",
    "MessageResponse",
    "PaginationParams",
]
