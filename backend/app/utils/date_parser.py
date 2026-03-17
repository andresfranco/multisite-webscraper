"""Date parsing utilities ported from the original scraper."""
from datetime import date, datetime
from typing import Optional
import structlog

logger = structlog.get_logger()

# Common date formats found in web articles (non-ISO 8601)
# ISO 8601 variants are handled separately via datetime.fromisoformat()
DATE_FORMATS = [
    "%Y-%m-%d",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
]


def parse_date(date_str: str) -> Optional[date]:
    """Parse a date string into a Python date object.

    Tries full ISO 8601 parsing first, then falls back to common date formats.
    Returns None if no format matches.
    Ported from WebScraper._parse_date() with additional format support.
    """
    if not date_str:
        return None

    # Clean up the string
    date_str = date_str.strip()

    # Try full ISO 8601 parsing first (handles timezones, T-separator, etc.)
    try:
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        pass

    # Strip timezone offset and T-component for remaining format attempts
    cleaned = date_str
    if "+" in cleaned and "T" in cleaned:
        cleaned = cleaned.split("+")[0]
    if "T" in cleaned and len(cleaned) > 10:
        cleaned = cleaned.split("T")[0]

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.date()
        except ValueError:
            continue

    logger.warning("date_parse_failed", date_str=date_str)
    return None
