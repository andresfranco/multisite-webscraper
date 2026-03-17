# Project Summary: Multisite Web Scraper

## Overview

A Python CLI application that scrapes article metadata (title, author, URL, publication date) from three tech education websites and stores results in a SQLite database. The project is production-ready with 32 passing tests, 61 articles collected, and full CLI control.

---

## Tech Stack

| Component       | Technology                              |
|-----------------|-----------------------------------------|
| Language        | Python 3.12+                            |
| Web Scraping    | requests, BeautifulSoup4                |
| Anti-Bot Bypass | cloudscraper (Cloudflare)               |
| ORM / Database  | SQLAlchemy 2.0+ / SQLite                |
| Concurrency     | concurrent.futures.ThreadPoolExecutor   |
| CLI             | argparse                                |
| Testing         | pytest                                  |

**Dependencies:** `requests`, `beautifulsoup4`, `sqlalchemy`, `cloudscraper`, `pytest`

---

## Architecture

```
main.py (CLI entry point)
  |
  v
webscraper_core/manager.py (Orchestrator)
  |-- Factory: _get_scraper_for_url() selects scraper by URL domain
  |-- Concurrency: ThreadPoolExecutor (configurable workers)
  |-- DB session: single shared session across all workers
  |
  +---> webscraper_core/scrapers/ (Site-specific extractors)
  |       |-- realpython_scraper.py   (RealPythonScraper extends WebScraper)
  |       |-- freecodecamp_scraper.py (FreeCodeCampScraper extends WebScraper)
  |       |-- datacamp_scraper.py     (DataCampScraper extends WebScraper, uses cloudscraper)
  |
  +---> webscraper_core/scraper.py (Base WebScraper class)
  |       |-- fetch_page()  - HTTP GET with requests
  |       |-- extract_article_data()  - dispatches to site-specific methods
  |       |-- _extract_generic_articles()  - fallback for unknown sites
  |       |-- _parse_date()  - multi-format date parser
  |
  +---> webscraper_core/repositories/ (Data access layer)
  |       |-- base_repository.py  (Generic CRUD, BaseRepository[T])
  |       |-- article_repository.py  (add_article_with_dedup, get_by_url)
  |       |-- author_repository.py   (get_or_create, CRUD)
  |
  +---> webscraper_core/models/ (SQLAlchemy ORM models)
  |       |-- base.py    (declarative_base)
  |       |-- author.py  (Author: author_id, name)
  |       |-- article.py (Article: article_id, title, author_id FK, url UNIQUE, publication_date)
  |
  +---> webscraper_core/database.py (Engine/session factory, create_tables)
  |
  +---> webscraper_core/analyzer.py (Title word-frequency analysis utility)
```

### Design Patterns

| Pattern              | Where                                | Purpose                                    |
|----------------------|--------------------------------------|--------------------------------------------|
| Repository Pattern   | `repositories/`                      | Encapsulate all DB access logic            |
| Factory Pattern      | `manager._get_scraper_for_url()`     | Select scraper class based on URL domain   |
| Specialist Pattern   | `scrapers/*_scraper.py`              | Site-specific HTML extraction logic        |
| Template Method      | `WebScraper` base -> subclass overrides | Common interface, specialized behavior   |
| Session Sharing      | `manager.run_many()`                 | Single DB session across thread workers    |

---

## Folder Structure

```
multisite-webscraper/
|-- main.py                          # CLI entry point
|-- README.md                        # Project readme
|-- .gitignore
|-- webscraper_core/                 # Core library
|   |-- __init__.py
|   |-- scraper.py                   # Base WebScraper class (353 lines)
|   |-- manager.py                   # Orchestration & concurrency (276 lines)
|   |-- analyzer.py                  # Title word-frequency analysis (37 lines)
|   |-- database.py                  # SQLAlchemy engine/session setup (57 lines)
|   |-- models/
|   |   |-- base.py                  # Declarative base
|   |   |-- author.py               # Author model
|   |   |-- article.py              # Article model
|   |-- repositories/
|   |   |-- base_repository.py      # Generic CRUD repository (99 lines)
|   |   |-- article_repository.py   # Article-specific queries (113 lines)
|   |   |-- author_repository.py    # Author-specific queries (81 lines)
|   |-- scrapers/
|       |-- realpython_scraper.py    # Real Python extractor (183 lines)
|       |-- freecodecamp_scraper.py  # FreeCodeCamp extractor (185 lines)
|       |-- datacamp_scraper.py      # DataCamp extractor + Cloudflare bypass (196 lines)
|-- tests/                           # 18 test files, 32 tests total
|-- docs/                            # 11 documentation files
```

---

## Current Features

1. **Multi-site scraping** - Real Python (19 articles), FreeCodeCamp (25 articles), DataCamp (17 articles)
2. **Concurrent processing** - Configurable thread workers (default 5) via `ThreadPoolExecutor`
3. **Smart deduplication** - Articles deduplicated by URL (unique constraint)
4. **Author linking** - get_or_create pattern prevents duplicate authors
5. **SQLite persistence** - Full ORM with SQLAlchemy, `scraper_data.db`
6. **Cloudflare bypass** - DataCamp uses `cloudscraper` library
7. **CLI interface** - `--urls` (required), `--workers`, `--mode normal|debug`
8. **Rate limiting** - Built-in delays (1-2 seconds) to avoid HTTP 429
9. **Generic fallback scraper** - Attempts extraction on unknown sites using common HTML patterns
10. **Word frequency analysis** - `analyzer.py` provides title text analysis

---

## How It Works

1. User runs `python main.py --urls <URL1> <URL2> ...`
2. `manager._get_scraper_for_url()` selects the appropriate scraper class per URL
3. Each scraper's `fetch_page()` retrieves HTML (DataCamp uses cloudscraper)
4. `extract_article_data()` parses HTML with BeautifulSoup using site-specific CSS selectors
5. Returns list of dicts: `{title, author, url, publication_date}`
6. `_save_articles_to_db()` persists via Repository pattern with URL deduplication
7. For Real Python, author is fetched from individual article detail pages (rate-limited)
8. Results are aggregated and displayed as CLI output

---

## Database Schema

```sql
CREATE TABLE author (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE article (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    publication_date DATE,
    FOREIGN KEY (author_id) REFERENCES author(author_id)
);
```

---

## Known Limitations

1. **Hardcoded site support** - Only 3 sites supported; adding a new site requires writing a new scraper class and registering it in the factory
2. **No web interface** - CLI only; no API or UI
3. **No scheduling** - Must be run manually or via external scheduler (Task Scheduler mentioned in docs)
4. **No retry logic** - Failed requests are not retried
5. **No proxy support** - Single IP, no proxy rotation
6. **No robots.txt compliance** - Does not check or respect robots.txt
7. **SQLite limitations** - Single-file database, not suitable for concurrent web server use
8. **No pagination** - Only scrapes the first/landing page of each site
9. **Fragile selectors** - CSS/attribute selectors will break when target sites change their HTML structure
10. **No content extraction** - Only collects metadata (title, author, URL, date), not article body text
11. **Limited error reporting** - Uses print statements, no structured logging
12. **No authentication/API** - No way to query results except by direct DB access or test scripts
13. **Thread safety concerns** - Single SQLAlchemy session shared across threads without explicit locking
