"""Pre-built ScrapeConfig templates for known sites.

These templates convert the existing hardcoded scrapers into ScrapeConfig
dictionaries that can be loaded into the database.
"""

TEMPLATES: dict[str, dict] = {
    "realpython": {
        "name": "Real Python Blog",
        "base_url": "https://realpython.com/",
        "use_headless_browser": False,
        "pagination_type": "none",
        "max_pages": 1,
        "item_selector": "div.card.border-0",
        "fields": [
            {
                "name": "title",
                "selector": "h2.card-title",
                "attribute": None,
                "transform": "strip",
                "required": True,
                "default_value": None,
            },
            {
                "name": "url",
                "selector": "a[href]",
                "attribute": "href",
                "transform": "to_absolute_url",
                "required": True,
                "default_value": None,
            },
            {
                "name": "publication_date",
                "selector": "span.mr-2",
                "attribute": None,
                "transform": "parse_date",
                "required": False,
                "default_value": None,
            },
        ],
        "request_delay_ms": 2000,
        "concurrent_requests": 1,
    },
    "freecodecamp": {
        "name": "freeCodeCamp News",
        "base_url": "https://www.freecodecamp.org/news/",
        "use_headless_browser": False,
        "pagination_type": "none",
        "max_pages": 1,
        "item_selector": "article.post-card",
        "fields": [
            {
                "name": "title",
                "selector": "h2",
                "attribute": None,
                "transform": "strip",
                "required": True,
                "default_value": "Untitled",
            },
            {
                "name": "url",
                "selector": "a[href]",
                "attribute": "href",
                "transform": "to_absolute_url",
                "required": True,
                "default_value": None,
            },
            {
                "name": "author",
                "selector": "span.author, span.post-author",
                "attribute": None,
                "transform": "strip",
                "required": False,
                "default_value": "Unknown",
            },
            {
                "name": "publication_date",
                "selector": "time",
                "attribute": "datetime",
                "transform": "parse_date",
                "required": False,
                "default_value": None,
            },
        ],
        "request_delay_ms": 1000,
        "concurrent_requests": 1,
    },
    "datacamp": {
        "name": "DataCamp Blog",
        "base_url": "https://www.datacamp.com/blog",
        "use_headless_browser": False,
        "pagination_type": "none",
        "max_pages": 1,
        "item_selector": "article.card, article.post, article.blog-card, div.card, div.post, div.blog-card",
        "fields": [
            {
                "name": "title",
                "selector": "h2, h3, a",
                "attribute": None,
                "transform": "strip",
                "required": True,
                "default_value": "Untitled",
            },
            {
                "name": "url",
                "selector": "a[href]",
                "attribute": "href",
                "transform": "to_absolute_url",
                "required": True,
                "default_value": None,
            },
            {
                "name": "author",
                "selector": "span.author, span.by-line, p.author, p.by-line",
                "attribute": None,
                "transform": "strip",
                "required": False,
                "default_value": "Unknown",
            },
            {
                "name": "publication_date",
                "selector": "time",
                "attribute": "datetime",
                "transform": "parse_date",
                "required": False,
                "default_value": None,
            },
        ],
        "request_delay_ms": 1000,
        "concurrent_requests": 1,
    },
}


def get_template(name: str) -> dict | None:
    """Get a ScrapeConfig template by name."""
    return TEMPLATES.get(name)


def list_templates() -> list[str]:
    """List all available template names."""
    return list(TEMPLATES.keys())
