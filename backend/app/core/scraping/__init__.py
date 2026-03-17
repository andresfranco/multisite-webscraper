"""Scraping engine and utilities."""
from app.core.scraping.engine import ScrapingEngine
from app.core.scraping.fetcher import fetch_page_http
from app.core.scraping.templates import TEMPLATES, get_template, list_templates

__all__ = ["ScrapingEngine", "fetch_page_http", "TEMPLATES", "get_template", "list_templates"]
