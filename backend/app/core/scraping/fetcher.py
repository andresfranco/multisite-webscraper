"""Page fetching strategies (HTTP and headless browser)."""
from typing import Optional

import httpx
import structlog

logger = structlog.get_logger()

# Default headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


async def fetch_page_http(
    url: str,
    headers: dict | None = None,
    timeout: float = 30.0,
) -> Optional[str]:
    """Fetch a page using httpx (async HTTP client).

    Args:
        url: The URL to fetch.
        headers: Optional custom headers to use.
        timeout: Request timeout in seconds.

    Returns:
        HTML content as string, or None on failure.
    """
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
        ) as client:
            response = await client.get(url, headers=merged_headers)
            response.raise_for_status()
            logger.info("page_fetched", url=url, status=response.status_code)
            return response.text
    except httpx.TimeoutException:
        logger.warning("fetch_timeout", url=url)
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("fetch_http_error", url=url, status=e.response.status_code)
        return None
    except httpx.HTTPError as e:
        logger.error("fetch_error", url=url, error=str(e))
        return None


async def fetch_page_playwright(
    url: str,
    wait_for_selector: str | None = None,
    headers: dict | None = None,
    timeout: float = 30.0,
) -> Optional[str]:
    """Fetch a page using Playwright and return rendered HTML."""
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("playwright_not_installed", url=url)
        return None

    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    browser = None
    context = None
    page = None

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(extra_http_headers=merged_headers)
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=int(timeout * 1000))
            if wait_for_selector:
                await page.wait_for_selector(
                    wait_for_selector,
                    timeout=int(timeout * 1000),
                )
            content = await page.content()
            logger.info("page_fetched_playwright", url=url)
            return content
    except PlaywrightTimeoutError:
        logger.warning("fetch_playwright_timeout", url=url)
        return None
    except Exception as e:
        logger.error("fetch_playwright_error", url=url, error=str(e))
        return None
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:
                pass
        if context is not None:
            try:
                await context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass


async def fetch_page(
    url: str,
    use_playwright: bool = False,
    wait_for_selector: str | None = None,
    headers: dict | None = None,
    timeout: float = 30.0,
) -> Optional[str]:
    """Fetch a page using the configured strategy."""
    if use_playwright:
        html = await fetch_page_playwright(
            url=url,
            wait_for_selector=wait_for_selector,
            headers=headers,
            timeout=timeout,
        )
        if html is not None:
            return html

    return await fetch_page_http(url=url, headers=headers, timeout=timeout)
