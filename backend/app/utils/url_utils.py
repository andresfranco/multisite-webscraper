"""URL normalization and SSRF-safety helpers."""
from __future__ import annotations

import ipaddress
from urllib.parse import urljoin, urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize a URL by standardizing scheme/host and removing fragments."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))


def extract_domain(url: str) -> str:
    """Extract the netloc from a URL."""
    return urlparse(url).netloc.lower()


def is_safe_url(url: str) -> bool:
    """Return True when a URL targets a public http(s) endpoint."""
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        return False

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        return False

    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        return False

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return True

    blocked = (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )
    return not blocked


def make_absolute(url: str, base_url: str) -> str:
    """Convert a relative URL to absolute using a base URL."""
    return urljoin(base_url, url)
