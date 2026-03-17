"""Pydantic schemas for ScrapeConfig API endpoints."""
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class FieldConfigSchema(BaseModel):
    """Schema for a single field extraction rule."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Field name (e.g. 'title', 'author')",
    )
    selector: str = Field(..., min_length=1, description="CSS selector or XPath expression")
    attribute: Optional[str] = Field(
        None, description="HTML attribute to extract (None = text content)"
    )
    transform: Optional[str] = Field(
        None,
        description="Transform to apply (e.g. 'strip', 'parse_date', 'to_absolute_url')",
    )
    required: bool = Field(True, description="Whether this field is required")
    default_value: Optional[str] = Field(None, description="Default value if extraction fails")


class ScrapeConfigCreate(BaseModel):
    """Schema for creating a new ScrapeConfig."""

    name: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., min_length=1, max_length=2048)

    # Page fetching
    use_headless_browser: bool = False
    wait_for_selector: Optional[str] = None
    custom_headers: Optional[dict] = None

    # Pagination
    pagination_type: str = Field("none", pattern="^(none|next_link|scroll|page_param)$")
    pagination_selector: Optional[str] = None
    max_pages: int = Field(1, ge=1, le=1000)

    # Item extraction
    item_selector: str = Field(..., min_length=1, max_length=500)
    fields: list[FieldConfigSchema] = Field(..., min_length=1)

    # Rate limiting
    request_delay_ms: int = Field(1000, ge=0, le=60000)
    concurrent_requests: int = Field(1, ge=1, le=10)

    # Scheduling
    schedule_cron: Optional[str] = None
    is_active: bool = True

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")
        return v

    @property
    def domain(self) -> str:
        """Extract domain from base_url."""

        return urlparse(self.base_url).netloc


class ScrapeConfigUpdate(BaseModel):
    """Schema for updating an existing ScrapeConfig. All fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = Field(None, min_length=1, max_length=2048)
    use_headless_browser: Optional[bool] = None
    wait_for_selector: Optional[str] = None
    custom_headers: Optional[dict] = None
    pagination_type: Optional[str] = Field(None, pattern="^(none|next_link|scroll|page_param)$")
    pagination_selector: Optional[str] = None
    max_pages: Optional[int] = Field(None, ge=1, le=1000)
    item_selector: Optional[str] = Field(None, min_length=1, max_length=500)
    fields: Optional[list[FieldConfigSchema]] = None
    request_delay_ms: Optional[int] = Field(None, ge=0, le=60000)
    concurrent_requests: Optional[int] = Field(None, ge=1, le=10)
    schedule_cron: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")
        return v


class ScrapeConfigResponse(BaseModel):
    """Schema for ScrapeConfig API responses."""

    id: int
    name: str
    base_url: str
    domain: str
    use_headless_browser: bool
    wait_for_selector: Optional[str]
    custom_headers: Optional[dict]
    pagination_type: str
    pagination_selector: Optional[str]
    max_pages: int
    item_selector: str
    fields: list[FieldConfigSchema] | dict
    request_delay_ms: int
    concurrent_requests: int
    schedule_cron: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
