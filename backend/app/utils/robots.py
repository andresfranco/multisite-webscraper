"""robots.txt utilities with in-memory caching."""
from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
import structlog

USER_AGENT = "MultiSiteScraperBot/1.0"
CACHE_TTL_SECONDS = 3600

logger = structlog.get_logger()

_robots_cache: dict[str, tuple[float, RobotFileParser]] = {}


async def _get_robot_parser(url: str) -> RobotFileParser | None:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if not domain:
        return None

    now = time.time()
    cached = _robots_cache.get(domain)
    if cached and cached[0] > now:
        return cached[1]

    robots_url = urljoin(f"{parsed.scheme}://{domain}", "/robots.txt")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(robots_url, headers={"User-Agent": USER_AGENT})
            if response.status_code == 404:
                return None
            response.raise_for_status()
    except Exception as e:
        logger.warning("robots_fetch_failed", url=robots_url, error=str(e))
        return None

    parser = RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())
        _robots_cache[domain] = (now + CACHE_TTL_SECONDS, parser)
        return parser
    except Exception as e:
        logger.warning("robots_parse_failed", url=robots_url, error=str(e))
        return None


async def is_allowed(url: str, user_agent: str = USER_AGENT) -> bool:
    """Check robots.txt and return True when scraping is allowed."""
    try:
        parser = await _get_robot_parser(url)
        if parser is None:
            return True
        return parser.can_fetch(user_agent, url)
    except Exception as e:
        logger.warning("robots_check_failed", url=url, error=str(e))
        return True


async def get_crawl_delay(url: str, user_agent: str = USER_AGENT) -> float | None:
    """Return the crawl-delay from robots.txt when available."""
    try:
        parser = await _get_robot_parser(url)
        if parser is None:
            return None
        delay = parser.crawl_delay(user_agent)
        return float(delay) if delay is not None else None
    except Exception as e:
        logger.warning("robots_crawl_delay_failed", url=url, error=str(e))
        return None
