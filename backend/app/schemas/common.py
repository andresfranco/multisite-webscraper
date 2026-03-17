"""Common/shared Pydantic schemas."""
from typing import Any, Optional

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: Optional[Any] = None


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = 1
    page_size: int = 20
