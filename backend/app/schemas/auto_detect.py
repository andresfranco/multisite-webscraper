"""Schemas for auto-detect scraping configuration endpoints."""
from pydantic import BaseModel, HttpUrl


class AutoDetectRequest(BaseModel):
    url: HttpUrl
    use_playwright: bool = False


class DetectedField(BaseModel):
    name: str
    selector: str
    attribute: str | None = None
    transform: str | None = None
    required: bool = True
    default_value: str | None = None


class AutoDetectResponse(BaseModel):
    url: str
    item_selector: str
    fields: list[DetectedField]
    confidence: float
    pagination_type: str
    pagination_selector: str | None = None
    detected_via: str
    preview_items: list[dict]
