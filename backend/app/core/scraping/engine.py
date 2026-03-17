import asyncio
import hashlib
import json
import re
import time
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import structlog

try:
    from lxml import etree, html as lxml_html
except ImportError:  # pragma: no cover - optional at runtime
    etree = None
    lxml_html = None

from app.core.scraping.fetcher import fetch_page
from app.utils.date_parser import parse_date
from app.utils.robots import get_crawl_delay, is_allowed
from app.utils.url_utils import extract_domain

logger = structlog.get_logger()


class ScrapingEngine:
    """Drives the scraping process using a ScrapeConfig dictionary."""

    _domain_last_request: dict[str, float] = {}

    def __init__(self, config: dict):
        """Initialize with a config dict (from ScrapeConfig model).

        Args:
            config: Dictionary with keys matching ScrapeConfig fields:
                - base_url, item_selector, fields, pagination_type,
                  pagination_selector, max_pages, request_delay_ms,
                  custom_headers, use_headless_browser, wait_for_selector
        """
        self.config = config
        self.base_url = config["base_url"]
        self.item_selector = config["item_selector"]
        self.fields = config.get("fields", [])
        self.pagination_type = config.get("pagination_type", "none")
        self.pagination_selector = config.get("pagination_selector")
        self.max_pages = config.get("max_pages", 1)
        self.request_delay_ms = config.get("request_delay_ms", 1000)
        self.custom_headers = config.get("custom_headers")
        self.use_headless = config.get("use_headless_browser", False)

    async def run(self, progress_callback=None) -> dict:
        """Execute the full scraping process.

        Args:
            progress_callback: Optional async callable(progress_dict) for updates.

        Returns:
            Dict with keys: items, pages_scraped, items_found, errors
        """
        all_items: list[dict] = []
        pages_scraped = 0
        errors = 0
        current_url = self.base_url
        domain = extract_domain(self.base_url)

        allowed = await is_allowed(self.base_url)
        if not allowed:
            logger.warning("scrape_blocked_by_robots", url=self.base_url)
            return {
                "items": [],
                "pages_scraped": 0,
                "items_found": 0,
                "errors": 1,
                "error_message": "Blocked by robots.txt",
            }

        crawl_delay = await get_crawl_delay(self.base_url)
        effective_delay_s = self.request_delay_ms / 1000.0
        if crawl_delay is not None and crawl_delay > effective_delay_s:
            effective_delay_s = crawl_delay

        for page_num in range(1, self.max_pages + 1):
            if not current_url:
                break

            logger.info("scraping_page", url=current_url, page=page_num)

            await self._enforce_domain_rate_limit(domain, effective_delay_s)

            # Fetch the page
            html = await fetch_page(
                url=current_url,
                use_playwright=self.use_headless,
                wait_for_selector=self.config.get("wait_for_selector"),
                headers=self.custom_headers,
            )
            if html is None:
                errors += 1
                logger.error("page_fetch_failed", url=current_url)
                break

            self._domain_last_request[domain] = time.monotonic()

            pages_scraped += 1

            # Parse and extract items
            soup = BeautifulSoup(html, "html.parser")
            page_items = self._extract_items(soup, current_url)
            all_items.extend(page_items)

            logger.info(
                "page_scraped",
                url=current_url,
                items_found=len(page_items),
                total_items=len(all_items),
            )

            # Report progress
            if progress_callback:
                await progress_callback({
                    "pages_scraped": pages_scraped,
                    "pages_total": self.max_pages,
                    "items_found": len(all_items),
                    "current_url": current_url,
                    "errors": errors,
                })

            # Find next page URL
            next_url = self._get_next_page_url(soup, current_url, page_num)
            if next_url == current_url or next_url is None:
                break
            current_url = next_url

            # Rate limiting
            if effective_delay_s > 0 and page_num < self.max_pages:
                await asyncio.sleep(effective_delay_s)

        return {
            "items": all_items,
            "pages_scraped": pages_scraped,
            "items_found": len(all_items),
            "errors": errors,
        }

    def _extract_items(self, soup: BeautifulSoup, page_url: str) -> list[dict]:
        """Extract all items from a parsed page using the config selectors."""
        items = []
        containers = self._select_containers(soup, self.item_selector)

        for container in containers:
            item_data = {}
            item_url = None
            skip = False

            for field in self.fields:
                value = self._extract_field(container, field, page_url)

                if value is None and field.get("required", True):
                    skip = True
                    break

                if value is None:
                    value = field.get("default_value")

                item_data[field["name"]] = value

                # Track item_url if field is named 'url' or 'link'
                if field["name"] in ("url", "link") and value:
                    item_url = value

            if skip:
                continue

            # Compute content hash
            content_hash = self._compute_hash(item_data)

            items.append({
                "data": item_data,
                "source_url": page_url,
                "item_url": item_url,
                "content_hash": content_hash,
            })

        return items

    async def _enforce_domain_rate_limit(self, domain: str, delay_s: float) -> None:
        """Throttle requests per domain within the current worker process."""
        if delay_s <= 0 or not domain:
            return

        last_request = self._domain_last_request.get(domain)
        if last_request is None:
            return

        elapsed = time.monotonic() - last_request
        remaining = delay_s - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)

    def _extract_field(
        self, container: Any, field: dict, page_url: str
    ) -> Optional[str]:
        """Extract a single field value from a container element."""
        selector = field["selector"]
        attribute = field.get("attribute")
        transform = field.get("transform")

        value = None

        if self._is_xpath(selector):
            value = self._extract_xpath_value(container, selector, attribute)

        if value is None:
            try:
                elem = container.select_one(selector)
            except Exception:
                return None

            if elem is None:
                return None

            if attribute:
                if attribute.startswith("json_ld:"):
                    value = self._extract_json_ld_value(elem.get_text(), attribute)
                else:
                    value = elem.get(attribute)
            else:
                value = elem.get_text(strip=True)

        if value is None:
            return None

        # Apply transforms
        if transform:
            value = self._apply_transform(value, transform, page_url)

        return value

    def _select_containers(self, soup: BeautifulSoup, selector: str) -> list[Any]:
        """Select item containers via CSS or XPath."""
        if self._is_xpath(selector):
            try:
                if etree is None or lxml_html is None:
                    logger.warning("xpath_support_unavailable")
                    return []
                document = lxml_html.fromstring(str(soup))
                matches = document.xpath(selector)
                return [BeautifulSoup(etree.tostring(match), "html.parser") for match in matches if isinstance(match, etree._Element)]
            except Exception:
                logger.warning("item_xpath_selection_failed", selector=selector)
                return []

        try:
            return soup.select(selector)
        except Exception:
            logger.warning("item_css_selection_failed", selector=selector)
            return []

    @staticmethod
    def _is_xpath(selector: str) -> bool:
        return selector.startswith("//") or selector.startswith("./")

    def _extract_xpath_value(
        self,
        container: Any,
        selector: str,
        attribute: str | None,
    ) -> Optional[str]:
        """Extract a field using XPath from a BeautifulSoup container."""
        if etree is None or lxml_html is None:
            logger.warning("xpath_support_unavailable")
            return None
        try:
            document = lxml_html.fromstring(str(container))
            results = document.xpath(selector)
        except Exception:
            logger.warning("field_xpath_failed", selector=selector)
            return None

        if not results:
            return None

        first = results[0]
        if isinstance(first, (etree._ElementUnicodeResult, str)):
            value = str(first).strip()
            return value or None

        if not isinstance(first, etree._Element):
            value = str(first).strip()
            return value or None

        if attribute:
            if attribute.startswith("json_ld:"):
                value = self._extract_json_ld_value("".join(first.itertext()), attribute)
            else:
                value = first.get(attribute)
        else:
            value = " ".join(first.itertext()).strip()
        return value or None

    def _extract_json_ld_value(self, raw_json: str, attribute: str) -> Optional[str]:
        """Extract a nested value from JSON-LD script content."""
        try:
            payload = json.loads(raw_json)
        except Exception:
            return None

        key_path = attribute.split(":", 1)[1]
        current: Any = payload
        for part in key_path.split("."):
            if isinstance(current, list):
                current = next((item for item in current if isinstance(item, dict) and part in item), current[0] if current else None)
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        if isinstance(current, dict):
            current = current.get("name") or current.get("@id") or current.get("url")
        if isinstance(current, list):
            current = current[0] if current else None
        return str(current).strip() if current not in (None, "") else None

    def _apply_transform(
        self, value: str, transform: str, page_url: str
    ) -> Optional[str]:
        """Apply a named transform to a field value."""
        if transform == "strip":
            return value.strip()
        elif transform == "parse_date":
            parsed = parse_date(value)
            return parsed.isoformat() if parsed else value
        elif transform == "to_absolute_url":
            if value.startswith(("http://", "https://")):
                return value
            return urljoin(page_url, value)
        elif transform.startswith("regex:"):
            pattern = transform[6:]
            match = re.search(pattern, value)
            return match.group(1) if match and match.groups() else (match.group(0) if match else value)
        elif transform == "lowercase":
            return value.lower()
        elif transform == "uppercase":
            return value.upper()
        else:
            return value

    def _get_next_page_url(
        self, soup: BeautifulSoup, current_url: str, current_page: int
    ) -> Optional[str]:
        """Determine the next page URL based on pagination config."""
        if self.pagination_type == "none":
            return None

        if self.pagination_type == "next_link" and self.pagination_selector:
            next_elem = soup.select_one(self.pagination_selector)
            if next_elem and next_elem.get("href"):
                href = next_elem["href"]
                return urljoin(current_url, href)
            return None

        if self.pagination_type == "page_param":
            # Append or increment page parameter
            parsed = urlparse(current_url)
            # Simple approach: replace or add page= parameter
            base = current_url.split("?")[0]
            next_page = current_page + 1
            separator = "?" if "?" not in current_url else "&"
            # Check if page param already exists
            if "page=" in current_url:
                import re as re_mod
                return re_mod.sub(
                    r"page=\d+", f"page={next_page}", current_url
                )
            return f"{base}{separator}page={next_page}"

        return None

    @staticmethod
    def _compute_hash(data: dict) -> str:
        """Compute SHA-256 hash of the item data for deduplication."""
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
