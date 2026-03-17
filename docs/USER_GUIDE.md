# Multisite Web Scraper — Complete User Guide

**Version**: 1.0.0 (CLI) / Web App (in progress)  
**Last Updated**: March 2026  
**Audience**: End users and developers

---

## Table of Contents

1. [Overview](#overview)
2. [Project Architecture](#project-architecture)
3. [Part 1 — CLI Scraper (Production Ready)](#part-1--cli-scraper-production-ready)
   - [Requirements](#requirements)
   - [Installation](#installation)
   - [Project Structure](#project-structure)
   - [Running the Scraper](#running-the-scraper)
   - [CLI Arguments Reference](#cli-arguments-reference)
   - [Output Format](#output-format)
   - [Database](#database)
   - [Verifying Results](#verifying-results)
   - [Running Tests](#running-tests)
   - [How It Works Internally](#how-it-works-internally)
   - [Adding a New Site (Developer)](#adding-a-new-site-developer)
   - [Known Limitations](#known-limitations)
   - [Troubleshooting](#troubleshooting-cli)
4. [Part 2 — Web App (In Progress)](#part-2--web-app-in-progress)
   - [Architecture Overview](#architecture-overview)
   - [Requirements](#requirements-web-app)
   - [Configuration](#configuration)
   - [Running with Docker (Recommended)](#running-with-docker-recommended)
   - [Running Without Docker (Manual)](#running-without-docker-manual)
   - [API Reference](#api-reference)
   - [Scrape Configurations](#scrape-configurations)
   - [Auto-Detection Engine](#auto-detection-engine)
   - [Scraping Engine Internals](#scraping-engine-internals)
   - [Jobs and Scheduling](#jobs-and-scheduling)
   - [Exporting Results](#exporting-results)
   - [Frontend](#frontend)
   - [Pre-Built Site Templates](#pre-built-site-templates)
   - [Troubleshooting](#troubleshooting-web-app)
5. [Appendix](#appendix)
   - [Glossary](#glossary)
   - [Dependencies Summary](#dependencies-summary)
   - [Documentation Map](#documentation-map)

---

## Overview

The **Multisite Web Scraper** is a tool for scraping articles from tech education websites and storing them in a database. It supports two usage modes:

- **CLI Scraper (v1.0.0, production-ready)** — A Python command-line tool that scrapes Real Python, FreeCodeCamp, and DataCamp from a single terminal command. Results are stored in a local SQLite database. No extra infrastructure is needed.

- **Web App (in progress)** — A full-stack application with a FastAPI REST API, Celery async workers, PostgreSQL, Redis, and a React frontend. It replaces hardcoded site support with configurable scrape definitions and adds scheduling, real-time job monitoring, and multi-format exports.

Both layers share the same repository. The CLI layer is stable and ready for use today. The web app layer is under active development.

---

## Project Architecture

```
multisite-webscraper/
├── main.py                     # CLI entry point
├── webscraper_core/            # CLI scraper package
│   ├── manager.py              # Orchestration, concurrency, DB save
│   ├── scraper.py              # Base WebScraper class
│   ├── database.py             # SQLAlchemy session factory
│   ├── analyzer.py             # Word frequency analysis utility
│   ├── models/                 # ORM models (Author, Article)
│   ├── repositories/           # Repository pattern (CRUD helpers)
│   └── scrapers/               # Site-specific scraper subclasses
│       ├── realpython_scraper.py
│       ├── freecodecamp_scraper.py
│       └── datacamp_scraper.py
│
├── backend/                    # FastAPI web app (in progress)
│   ├── app/
│   │   ├── main.py             # FastAPI app factory
│   │   ├── config.py           # Pydantic BaseSettings
│   │   ├── api/v1/             # REST API routes
│   │   ├── core/scraping/      # Universal scraping engine
│   │   ├── models/             # SQLAlchemy async models
│   │   ├── repositories/       # Async CRUD repositories
│   │   └── schemas/            # Pydantic request/response schemas
│   ├── celery_app.py           # Celery worker + beat configuration
│   ├── alembic/                # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React + Vite frontend (in progress)
│   ├── src/
│   │   ├── App.tsx             # Route definitions
│   │   ├── pages/              # UI pages (Dashboard, Configs, Jobs, etc.)
│   │   └── api/                # Typed API client wrappers
│   └── Dockerfile
│
├── docker-compose.yml          # Development Docker setup
├── docker-compose.prod.yml     # Production Docker setup
├── tests/                      # CLI test suite (32 passing)
└── docs/                       # All documentation
```

---

## Part 1 — CLI Scraper (Production Ready)

### Requirements

- Python 3.8 or higher
- pip
- Internet access to the target websites

No Docker, no database server, no environment variables required.

---

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/andresfranco/multisite-webscraper.git
cd multisite-webscraper

# 2. (Recommended) Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install requests beautifulsoup4 sqlalchemy cloudscraper pytest
```

The SQLite database (`scraper_data.db`) is created automatically the first time you run the scraper. No manual database setup is needed.

---

### Project Structure

The CLI layer lives in two places:

| Path | Purpose |
|------|---------|
| `main.py` | Entry point — parses CLI arguments and calls the manager |
| `webscraper_core/manager.py` | Orchestrates scraping across multiple URLs in parallel |
| `webscraper_core/scraper.py` | Base `WebScraper` class with shared fetch/parse logic |
| `webscraper_core/scrapers/` | Site-specific subclasses for Real Python, FreeCodeCamp, DataCamp |
| `webscraper_core/models/` | SQLAlchemy ORM models (`Author`, `Article`) |
| `webscraper_core/repositories/` | Repository pattern wrappers around SQLAlchemy queries |
| `webscraper_core/database.py` | Creates and returns the SQLAlchemy session factory |
| `webscraper_core/analyzer.py` | Utility for word frequency analysis on article titles |
| `tests/` | 32 unit and integration tests |

---

### Running the Scraper

#### Scrape all three default sites

```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog
```

#### Scrape a single site

```bash
python main.py --urls https://realpython.com/
```

#### Scrape multiple sites with a custom worker count

```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news --workers 3
```

#### Enable verbose debug output

```bash
python main.py --urls https://realpython.com/ --mode debug
```

#### Show all available options

```bash
python main.py --help
```

---

### CLI Arguments Reference

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--urls URL [URL ...]` | Yes | — | One or more full URLs to scrape |
| `--workers N` | No | `5` | Number of concurrent worker threads |
| `--mode normal\|debug` | No | `normal` | Output verbosity level |

**`--urls`**

Accepts one or more space-separated URLs. All URLs are processed in parallel by the worker pool.

```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news
```

If `--urls` is omitted, the program exits immediately with:
```
main.py: error: the following arguments are required: --urls
```

**`--workers`**

Controls how many threads run simultaneously. Use fewer workers on machines with limited resources. Going above 10 risks system overload or getting rate-limited by target sites.

| Range | Behaviour |
|-------|-----------|
| 1–3 | Conservative, low resource usage |
| 5 (default) | Balanced |
| 6–10 | Faster, higher memory/CPU usage |

**`--mode`**

- `normal` (default) — prints target URLs, worker count, per-site results, and aggregate stats.
- `debug` — adds a debug banner and CLI configuration summary at the top of the output.

---

### Output Format

#### Normal mode

```
======================================================================
Tech Trends Database Scraper - Multi-Site Collection
======================================================================

Target websites: 3
  1. https://realpython.com/
  2. https://www.freecodecamp.org/news
  3. https://www.datacamp.com/blog

Worker threads: 5

======================================================================
DETAILED RESULTS BY WEBSITE
======================================================================

[OK] https://realpython.com/
   Created: 19 articles
   Skipped: 0 duplicates

[OK] https://www.freecodecamp.org/news
   Created: 25 articles
   Skipped: 0 duplicates

[OK] https://www.datacamp.com/blog
   Created: 17 articles
   Skipped: 0 duplicates

======================================================================
AGGREGATED STATISTICS
======================================================================

Total URLs Processed: 3
Successful: 3
Failed: 0

Total Articles:
  Created: 61
  Skipped (duplicates): 0
  Errors: 0
  Total Processed: 61

======================================================================
```

On subsequent runs, already-stored articles appear in the `Skipped (duplicates)` count. Deduplication is based on the article URL — each URL is stored only once.

#### Debug mode

Debug mode prepends a configuration block before the normal output:

```
======================================================================
DEBUG MODE ENABLED - Verbose logging active
======================================================================

CLI Configuration:
  URLs to scrape: 3
  Worker threads: 5
  Output mode: debug

[... rest of normal output ...]
```

---

### Database

The CLI uses a local **SQLite** database (`scraper_data.db`) created automatically in the project root on the first run.

#### Schema

**`author` table**

| Column | Type | Notes |
|--------|------|-------|
| `author_id` | INTEGER | Primary key, auto-increment |
| `name` | VARCHAR(255) | Author display name |

**`article` table**

| Column | Type | Notes |
|--------|------|-------|
| `article_id` | INTEGER | Primary key, auto-increment |
| `title` | VARCHAR(255) | Article title |
| `author_id` | INTEGER | Foreign key → `author.author_id` |
| `url` | VARCHAR(500) | **UNIQUE** — deduplication key |
| `publication_date` | DATE | Nullable |

#### Accessing the database directly

Any SQLite browser (e.g., [DB Browser for SQLite](https://sqlitebrowser.org/)) can open `scraper_data.db`. You can also use the built-in verification scripts:

```bash
# Quick record count per table
python tests/check_db.py

# List all extracted articles
python tests/verify_scrape.py

# Full database health check
python tests/final_verification.py
```

#### Resetting the database

Delete the file and re-run the scraper:

```bash
del scraper_data.db      # Windows
rm scraper_data.db       # macOS / Linux

python main.py --urls https://realpython.com/ ...
```

---

### Verifying Results

After scraping, use the test utilities in `tests/`:

```bash
# Show article and author counts
python tests/check_db.py

# List every extracted article with title, author, date, URL
python tests/verify_scrape.py

# Comprehensive check: counts, relationships, data integrity
python tests/final_verification.py
```

---

### Running Tests

The test suite contains **32 tests** (23 unit + 9 CLI functional). All should pass on a clean install.

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_scraper.py -v
pytest tests/test_main_workflow.py -v

# Run site-specific scraper tests
pytest tests/test_realpython_scraper_new.py -v
pytest tests/test_freecodecamp_scraper_new.py -v
pytest tests/test_datacamp_scraper_new.py -v
```

Test coverage areas:
- Article extraction and parsing for all 3 sites
- Deduplication (URL-based)
- Database model relationships
- Author get-or-create logic
- CLI argument parsing and validation
- Error handling for bad URLs and failed fetches
- Concurrent processing with multiple workers

---

### How It Works Internally

#### High-level flow

```
main.py
  └─ run_many_and_aggregate(urls, max_workers)   # manager.py
       ├─ create SQLite session
       ├─ ThreadPoolExecutor (N workers)
       │    └─ _process_single(url, session)      # per thread
       │         ├─ _get_scraper_for_url(url)     # factory
       │         ├─ scraper.fetch_page()
       │         ├─ scraper.extract_article_data(html)
       │         └─ _save_articles_to_db(articles, url, session)
       │              ├─ AuthorRepository.get_or_create(name)
       │              └─ ArticleRepository.add_article_with_dedup(data, author)
       └─ aggregate_results(results)
```

#### Scraper factory

`_get_scraper_for_url()` in `manager.py` matches URL substrings to scraper classes:

| URL contains | Class used |
|-------------|-----------|
| `realpython.com` | `RealPythonScraper` |
| `freecodecamp.org` | `FreeCodeCampScraper` |
| `datacamp.com` | `DataCampScraper` |
| anything else | `WebScraper` (generic fallback) |

#### Site-specific scraper behaviours

**Real Python** (`webscraper_core/scrapers/realpython_scraper.py`)
- Scrapes the landing page for article cards using `div.card.border-0` containers
- Makes a secondary HTTP request to each article's detail page to fetch the author name (limited to the first 3 articles per run to avoid rate limiting; uses a 2-second delay between requests)
- Falls back to `"Unknown"` if the detail page fetch fails

**FreeCodeCamp** (`webscraper_core/scrapers/freecodecamp_scraper.py`)
- Scrapes `article.post-card` containers on the `/news` page
- Extracts title, URL, author, and publication date directly from the listing page

**DataCamp** (`webscraper_core/scrapers/datacamp_scraper.py`)
- Uses `cloudscraper` instead of `requests` to bypass Cloudflare bot protection
- Scrapes the `/blog` listing page for article cards

**Generic fallback** (`webscraper_core/scraper.py` — `_extract_generic_articles`)
- Attempts to extract articles from any unknown URL using common HTML patterns
- Results may be incomplete or inaccurate for unsupported sites

#### Deduplication

Before inserting a new article, `ArticleRepository.add_article_with_dedup()` queries for an existing row with the same `url`. If found, the article is skipped (counted as a duplicate). This relies on the `UNIQUE` constraint on the `article.url` column.

#### Concurrency model

All worker threads share a **single SQLAlchemy session** created once in `run_many()` before the thread pool starts, and closed in a `finally` block after all threads complete. This reduces database connection overhead but means all threads serialize their writes through the same session object.

---

### Adding a New Site (Developer)

To support a new website:

1. **Create a new scraper class** in `webscraper_core/scrapers/`:

```python
# webscraper_core/scrapers/mysite_scraper.py
from webscraper_core.scraper import WebScraper
from bs4 import BeautifulSoup

class MySiteScraper(WebScraper):
    def extract_article_data(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        for card in soup.select('div.article-card'):
            articles.append({
                'title': card.select_one('h2').get_text(strip=True),
                'url': card.select_one('a')['href'],
                'author': card.select_one('.author').get_text(strip=True),
                'publication_date': None,
            })
        return articles
```

2. **Register it in the factory** in `webscraper_core/manager.py`:

```python
from .scrapers.mysite_scraper import MySiteScraper

def _get_scraper_for_url(url: str) -> WebScraper:
    if 'realpython.com' in url:
        return RealPythonScraper(url)
    elif 'freecodecamp.org' in url:
        return FreeCodeCampScraper(url)
    elif 'datacamp.com' in url:
        return DataCampScraper(url)
    elif 'mysite.com' in url:          # <-- add this
        return MySiteScraper(url)
    else:
        return WebScraper(url)
```

3. **Write tests** for the new scraper in `tests/test_mysite_scraper.py`.

4. **Run** `pytest tests/ -v` to confirm no regressions.

---

### Known Limitations

| Limitation | Impact |
|-----------|--------|
| Only 3 hardcoded sites supported | Any other URL uses the generic fallback which may produce incomplete data |
| No pagination | Only the first landing page is scraped per run |
| No retry logic | A single failed HTTP request means no articles from that URL |
| No robots.txt compliance | The CLI does not check `robots.txt` before scraping |
| No proxy support | All requests come from the same IP address |
| Shared session without locking | Concurrent thread writes are not explicitly synchronized |
| CSS selector fragility | If a target site changes its HTML structure, the selector will break |
| Real Python author fetch | Limited to first 3 articles to avoid rate limiting |

---

### Troubleshooting (CLI)

**No articles extracted**
- Verify the URL is accessible in a browser
- Run with `--mode debug` for more verbose output
- Check if the site is returning a Cloudflare challenge page (only DataCamp has built-in handling for this)

**Import errors on startup**
```bash
pip install requests beautifulsoup4 sqlalchemy cloudscraper
```

**Database errors**
- Delete `scraper_data.db` and re-run. The schema is recreated automatically.

**Slow scraping**
- Increase workers: `--workers 8`
- Note: Real Python has a built-in 2-second delay for author fetches that cannot be disabled via CLI

**`--workers` value is ignored for site sequencing**
- Workers affect how many URLs are fetched in parallel, not how fast a single URL is processed. With only one URL, the worker count has no effect.

---

## Part 2 — Web App (In Progress)

> **Status notice**: The web app layer is actively being developed. The architecture and API are defined and the code is partially written. Treat this section as a reference for the intended design. Not all features may be fully functional yet.

---

### Architecture Overview

```
Browser
  └─ React Frontend (Vite, port 5173 / 3000)
       └─ HTTP / WebSocket
            └─ FastAPI Backend (uvicorn, port 8000)
                 ├─ PostgreSQL (SQLAlchemy async + asyncpg)
                 ├─ Redis (job queue + result backend)
                 └─ Celery Workers
                      └─ ScrapingEngine (CSS/XPath, Playwright, pagination)
```

**Services (Docker)**

| Service | Image / Build | Port | Purpose |
|---------|--------------|------|---------|
| `api` | `./backend` | 8000 | FastAPI REST API |
| `worker` | `./backend` | — | Celery task worker |
| `beat` | `./backend` | — | Celery beat scheduler |
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL database |
| `redis` | `redis:7-alpine` | 6379 | Message broker + cache |

---

### Requirements (Web App)

- Docker Desktop (recommended) **or** Python 3.11+ and Node 20+ for manual setup
- 2 GB+ free RAM for Docker
- Ports 8000, 5432, and 6379 available

---

### Configuration

The backend reads configuration from environment variables (or a `.env` file in the `backend/` directory). Copy the example file to get started:

```bash
cp backend/.env.example backend/.env
```

**Available environment variables**

| Variable | Default (Docker) | Description |
|----------|-----------------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://scraper:scraper@db:5432/scraper` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | JWT signing key — **change in production** |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT token lifetime in minutes |
| `DEBUG` | `true` | Enable FastAPI debug mode |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed CORS origins |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/1` | Celery result store |

> For production, always set a strong random `SECRET_KEY` and set `DEBUG=false`.

---

### Running with Docker (Recommended)

```bash
# Start all services in the background
docker compose up -d

# Follow logs
docker compose logs -f

# Run database migrations
docker compose exec api alembic upgrade head

# Stop all services
docker compose down
```

After starting, the API is available at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

**Production deployment**

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

The production compose file adds an Nginx reverse proxy and enables network isolation between services.

---

### Running Without Docker (Manual)

**Backend**

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Install Playwright browser binaries (required for headless scraping)
playwright install chromium

# 4. Start PostgreSQL and Redis manually (or via Docker for just those services)
docker compose up -d db redis

# 5. Set environment variables
cp backend/.env.example backend/.env
# Edit backend/.env as needed

# 6. Run database migrations
cd backend
alembic upgrade head

# 7. Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 8. In a separate terminal: start the Celery worker
celery -A celery_app worker --loglevel=info --concurrency=2

# 9. In a separate terminal: start Celery beat (scheduler)
celery -A celery_app beat --loglevel=info
```

**Frontend**

```bash
cd frontend
npm install
npm run dev        # development server on http://localhost:5173
npm run build      # production build to frontend/dist/
```

---

### API Reference

All endpoints are prefixed with `/api/v1`. Interactive documentation is available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc) when the server is running.

#### Authentication — `/api/v1/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create a new user account |
| POST | `/auth/login` | No | Log in and receive a JWT token |
| GET | `/auth/me` | JWT | Get the current user's profile |
| POST | `/auth/change-password` | JWT | Change the current user's password |
| POST | `/auth/api-key` | JWT | Generate (or regenerate) an API key |
| DELETE | `/auth/api-key` | JWT | Revoke the current API key |

**Register example**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "myuser", "password": "mypassword"}'
```

**Login example**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
# Returns: {"access_token": "...", "expires_in": 3600, "user": {...}}
```

Use the returned `access_token` in subsequent requests:
```bash
-H "Authorization: Bearer <access_token>"
```

---

#### Scrape Configurations — `/api/v1/configs`

A **ScrapeConfig** defines how to extract data from a website: which URL to fetch, which HTML containers to look for, which fields to extract from each container, and how to paginate.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/configs/` | List all configurations (supports `offset`, `limit`) |
| POST | `/configs/` | Create a new configuration |
| GET | `/configs/{id}` | Get a single configuration |
| PUT | `/configs/{id}` | Update a configuration |
| DELETE | `/configs/{id}` | Delete a configuration |
| POST | `/configs/{id}/test` | Test a config against one page (no DB writes) |
| POST | `/configs/auto-detect` | Auto-detect a config from a URL |

**ScrapeConfig fields**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable name |
| `base_url` | string | Starting URL to scrape |
| `item_selector` | string | CSS selector or XPath for article containers |
| `fields` | array | List of field definitions (see below) |
| `use_headless_browser` | bool | Use Playwright for JavaScript-rendered pages |
| `wait_for_selector` | string\|null | CSS selector to wait for before extracting (headless only) |
| `pagination_type` | string | `none`, `next_link`, or `page_param` |
| `pagination_selector` | string\|null | CSS selector for the "next page" link |
| `max_pages` | integer | Maximum pages to scrape (default: 1) |
| `request_delay_ms` | integer | Delay between requests in milliseconds |
| `concurrent_requests` | integer | Max concurrent requests (default: 1) |
| `custom_headers` | object\|null | Additional HTTP headers |
| `schedule_cron` | string\|null | Cron expression for automatic scheduling |
| `is_active` | bool | Whether the config is enabled |

**Field definition**

Each entry in the `fields` array describes one piece of data to extract from each item container:

| Sub-field | Type | Description |
|-----------|------|-------------|
| `name` | string | Key name in the output data |
| `selector` | string | CSS selector or XPath to find the element |
| `attribute` | string\|null | HTML attribute to read (e.g., `href`, `datetime`). Omit to read text content. |
| `transform` | string\|null | Post-processing: `strip`, `parse_date`, `to_absolute_url`, `lowercase`, `uppercase`, `regex:<pattern>` |
| `required` | bool | If `true`, items missing this field are skipped |
| `default_value` | string\|null | Fallback value when the field is not found |

**Create config example**

```bash
curl -X POST http://localhost:8000/api/v1/configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Blog",
    "base_url": "https://example.com/blog",
    "item_selector": "article.post",
    "fields": [
      {"name": "title", "selector": "h2", "transform": "strip", "required": true},
      {"name": "url",   "selector": "a",  "attribute": "href", "transform": "to_absolute_url", "required": true},
      {"name": "date",  "selector": "time","attribute": "datetime", "transform": "parse_date", "required": false}
    ],
    "pagination_type": "next_link",
    "pagination_selector": "a.next-page",
    "max_pages": 5,
    "request_delay_ms": 1000,
    "is_active": true
  }'
```

---

#### Scrape Jobs — `/api/v1/jobs`

A **ScrapeJob** is a single execution run of a ScrapeConfig.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs/` | List jobs (filter by `status` or `config_id`) |
| POST | `/jobs/` | Start a new job for a config |
| GET | `/jobs/{id}` | Get a single job |
| POST | `/jobs/{id}/cancel` | Cancel a pending or running job |

**Job statuses**: `pending` → `running` → `completed` | `failed` | `cancelled`

**Start a job example**

```bash
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"config_id": 1}'
```

The job is dispatched to a Celery worker asynchronously. Poll `GET /jobs/{id}` to check status.

---

#### Scraped Results — `/api/v1/results`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/results/` | List results (filter by `config_id` or `job_id`, paginated) |
| GET | `/results/stats` | Aggregated statistics across all scraped data |
| GET | `/results/export` | Download results as JSON, CSV, or Excel |
| GET | `/results/{id}` | Get a single scraped item |
| DELETE | `/results/{id}` | Delete a scraped item |

**Export results example**

```bash
# JSON (default)
curl "http://localhost:8000/api/v1/results/export?format=json" -o results.json

# CSV
curl "http://localhost:8000/api/v1/results/export?format=csv" -o results.csv

# Excel
curl "http://localhost:8000/api/v1/results/export?format=xlsx" -o results.xlsx

# Filter by config
curl "http://localhost:8000/api/v1/results/export?format=csv&config_id=1" -o config1.csv
```

---

#### Schedules — `/api/v1/schedules`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/schedules` | List all schedules |
| POST | `/schedules` | Create a new schedule |
| GET | `/schedules/{id}` | Get a single schedule |
| PATCH | `/schedules/{id}` | Update a schedule (partial) |
| DELETE | `/schedules/{id}` | Delete a schedule |
| POST | `/schedules/{id}/trigger` | Manually trigger a schedule immediately |

**Create schedule example**

```bash
curl -X POST http://localhost:8000/api/v1/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Real Python scrape",
    "config_id": 1,
    "cron_expression": "0 6 * * *",
    "is_active": true
  }'
```

---

#### Other Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check — returns API and database status |
| GET | `/metrics` | Prometheus-compatible metrics |
| WS | `/ws` | WebSocket for real-time job progress updates |

---

### Scrape Configurations

Scrape configurations are the core concept of the web app. Instead of writing Python code for each new site, you define a JSON-style configuration that tells the engine what to look for.

#### Pagination types

| Type | Description | Required extra field |
|------|-------------|---------------------|
| `none` | Single page only | — |
| `next_link` | Follow a "Next" link | `pagination_selector` — CSS selector for the next-page anchor |
| `page_param` | Increment `?page=N` URL parameter | — |

#### Transform functions

Transforms are applied to extracted field values before storage:

| Transform | Description |
|-----------|-------------|
| `strip` | Remove leading/trailing whitespace |
| `parse_date` | Parse a date string into ISO 8601 format |
| `to_absolute_url` | Convert a relative URL to an absolute URL using the page URL as base |
| `lowercase` | Convert to lowercase |
| `uppercase` | Convert to uppercase |
| `regex:<pattern>` | Extract the first capture group from a regex pattern. Falls back to the full match if no groups are defined. |

#### XPath support

Field selectors that start with `//` or `./` are treated as XPath expressions (requires `lxml` to be installed, which is included in `backend/requirements.txt`).

---

### Auto-Detection Engine

The auto-detection endpoint (`POST /api/v1/configs/auto-detect`) analyzes a URL and attempts to generate a `ScrapeConfig` automatically, without requiring you to write any selectors by hand.

It tries four strategies in order, picks the one with the highest confidence score, and returns a config you can use directly or edit before saving:

| Strategy | Description | Confidence |
|----------|-------------|-----------|
| **JSON-LD** | Reads `<script type="application/ld+json">` structured data (Article, BlogPosting, NewsArticle types) | High |
| **Open Graph** | Reads `<meta property="og:*">` tags | Medium |
| **RSS** | Detects `<link rel="alternate" type="application/rss+xml">` and fetches the feed | Medium |
| **Structural** | Inspects DOM for repeated container patterns with article-like class names | Variable |

**Auto-detect request**

```bash
curl -X POST http://localhost:8000/api/v1/configs/auto-detect \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/blog", "use_playwright": false}'
```

**Response shape**

```json
{
  "url": "https://example.com/blog",
  "item_selector": "article.post-card",
  "fields": [
    {"name": "title",  "selector": "h2", "transform": "strip", ...},
    {"name": "url",    "selector": "a",  "attribute": "href", "transform": "to_absolute_url", ...},
    {"name": "author", "selector": "span.author", "transform": "strip", ...}
  ],
  "confidence": 0.85,
  "pagination_type": "next_link",
  "pagination_selector": "a.next",
  "detected_via": "json_ld",
  "preview_items": [...]
}
```

Set `use_playwright: true` for JavaScript-rendered pages that require a headless browser to load their content.

---

### Scraping Engine Internals

The `ScrapingEngine` class (`backend/app/core/scraping/engine.py`) drives all web app scraping. It accepts a config dictionary and performs:

1. **robots.txt check** — Fetches and parses the target site's `robots.txt`. If the URL is disallowed, the run is aborted immediately with an error.
2. **Crawl delay enforcement** — Reads the `Crawl-delay` directive from `robots.txt` and uses the larger of the configured delay and the robots.txt delay.
3. **Page fetching** — Uses `httpx` for standard pages or `Playwright` (Chromium) for JavaScript-rendered pages.
4. **Item extraction** — Finds all containers matching `item_selector`, then extracts each configured field using CSS selectors or XPath.
5. **Field transforms** — Applies post-processing (strip, parse_date, to_absolute_url, regex, etc.) to raw extracted values.
6. **Deduplication hashing** — Computes a SHA-256 hash of each item's data dictionary for duplicate detection.
7. **Pagination** — Follows next-page links or increments page parameters up to `max_pages`.
8. **Progress callbacks** — Optionally sends real-time progress updates via a WebSocket callback.

---

### Jobs and Scheduling

**Manual jobs** are created via `POST /api/v1/jobs/` and dispatched immediately to a Celery worker.

**Scheduled jobs** are created via `POST /api/v1/schedules/` with a cron expression. Celery Beat reads the schedule table and fires jobs at the specified times.

Cron expression format: `minute hour day-of-month month day-of-week`

| Example cron | Meaning |
|-------------|---------|
| `0 6 * * *` | Every day at 06:00 |
| `0 */4 * * *` | Every 4 hours |
| `0 9 * * 1` | Every Monday at 09:00 |
| `*/30 * * * *` | Every 30 minutes |

A schedule can also be triggered manually at any time via `POST /api/v1/schedules/{id}/trigger`, which creates a new job and dispatches it immediately without waiting for the next scheduled time.

---

### Exporting Results

Results can be exported in three formats via `GET /api/v1/results/export`:

| Format | MIME type | Query param |
|--------|-----------|-------------|
| JSON | `application/json` | `format=json` |
| CSV | `text/csv` | `format=csv` |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `format=xlsx` |

Optional query parameters:
- `config_id=<id>` — export only results from a specific scrape config
- `job_id=<id>` — export only results from a specific job run

The CSV and Excel exports flatten the `data` JSONB field into individual `data_<fieldname>` columns.

---

### Frontend

The React frontend is located in `frontend/` and is built with:

- **React 18** + **TypeScript**
- **Vite** (build tool and dev server)
- **TanStack Query** (data fetching and caching)
- **React Router v6** (client-side routing)
- **Tailwind CSS** + **Radix UI** + **Shadcn/ui** (styling and components)
- **Recharts** (dashboard charts)
- **Axios** (HTTP client)

**Available pages**

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Overview metrics and recent activity charts |
| `/configs` | ConfigsList | Browse all scrape configurations |
| `/configs/new` | ConfigBuilder | Visual form to create a new config |
| `/configs/:id` | ConfigDetail | View and edit a single config |
| `/jobs` | JobsList | Browse all scrape jobs with status filtering |
| `/jobs/:id` | JobDetail | Real-time job progress and logs |
| `/results` | ResultsBrowser | Browse, search, and filter scraped items |
| `/results/:id` | ResultDetail | View a single scraped item's full data |
| `/export` | Export | Download results in JSON, CSV, or Excel |
| `/schedules` | SchedulesList | Browse all schedules |
| `/schedules/new` | ScheduleForm | Create a new schedule |
| `/login` | Login | Authentication |
| `/register` | Register | Create a new account |

Authentication-required routes redirect to `/login` when no valid JWT token is present.

---

### Pre-Built Site Templates

The file `backend/app/core/scraping/templates.py` contains ready-to-use `ScrapeConfig` definitions for the three original sites. These can be loaded into the database to immediately begin scraping without writing any selectors manually.

**Available templates**: `realpython`, `freecodecamp`, `datacamp`

To load a template programmatically:

```python
from app.core.scraping.templates import get_template

config_dict = get_template("realpython")
# Use config_dict to create a ScrapeConfig via the API or directly in the DB
```

---

### Troubleshooting (Web App)

**`docker compose up` fails — port already in use**

Check for processes using ports 8000, 5432, or 6379:
```bash
# Windows
netstat -ano | findstr :8000

# macOS / Linux
lsof -i :8000
```

**API returns 500 — database not ready**

Wait a few seconds for the `db` health check to pass, then retry. You can check service health with:
```bash
docker compose ps
```

**Celery worker not picking up jobs**

Verify Redis is running and that `CELERY_BROKER_URL` in the environment matches your Redis URL:
```bash
docker compose logs worker
docker compose logs redis
```

**Playwright / headless browser errors**

Ensure Playwright's Chromium binaries are installed:
```bash
docker compose exec api playwright install chromium
```

Or in a manual setup:
```bash
playwright install chromium
```

**JWT token rejected (401 Unauthorized)**

Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 minutes). Log in again to get a fresh token.

**`alembic upgrade head` fails**

Ensure `DATABASE_URL` is set correctly and the `db` service is healthy before running migrations.

---

## Appendix

### Glossary

| Term | Definition |
|------|-----------|
| **ScrapeConfig** | A JSON-style definition that tells the web app engine how to extract data from a specific website |
| **ScrapeJob** | A single execution instance of a ScrapeConfig |
| **ScrapedItem** | One row of data extracted by a job |
| **Item selector** | A CSS selector or XPath expression that identifies repeating containers (e.g., article cards) on a page |
| **Field** | One piece of data to extract from each container (e.g., title, URL, date) |
| **Transform** | A post-processing operation applied to a raw extracted value |
| **Deduplication** | The process of skipping items already stored (CLI: by URL; Web app: by content hash) |
| **Celery** | A distributed task queue used by the web app to run scrape jobs asynchronously |
| **Celery Beat** | The Celery scheduling component that fires tasks on a cron schedule |
| **Playwright** | A headless browser automation library used for JavaScript-rendered pages |
| **robots.txt** | A file served by websites that specifies which paths may be crawled by bots |
| **cloudscraper** | A Python library that bypasses Cloudflare bot protection |

---

### Dependencies Summary

#### CLI Layer

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | latest | HTTP client |
| `beautifulsoup4` | latest | HTML parsing |
| `sqlalchemy` | 2.x | ORM and SQLite session management |
| `cloudscraper` | latest | Cloudflare bypass (DataCamp) |
| `pytest` | latest | Testing framework |

#### Web App — Backend

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.6 | REST API framework |
| `uvicorn` | 0.34.0 | ASGI server |
| `sqlalchemy[asyncio]` | 2.0.36 | Async ORM |
| `asyncpg` | 0.30.0 | PostgreSQL async driver |
| `alembic` | 1.14.0 | Database migrations |
| `celery` | 5.4.0 | Async task queue |
| `redis` | 5.2.1 | Redis client |
| `beautifulsoup4` | 4.12.3 | HTML parsing |
| `httpx` | 0.28.1 | Async HTTP client |
| `pydantic` | 2.10.3 | Data validation |
| `pydantic-settings` | 2.7.0 | Environment-based config |
| `python-jose` | 3.3.0 | JWT creation and verification |
| `bcrypt` / `passlib` | 4.2.1 / 1.7.4 | Password hashing |
| `lxml` | 5.3.0 | XPath support |
| `structlog` | 24.4.0 | Structured logging |
| `playwright` | 1.49.0 | Headless browser |
| `openpyxl` | 3.1.5 | Excel export |
| `croniter` | 3.0.3 | Cron expression parsing |
| `email-validator` | 2.1.1 | Email validation for user registration |

#### Web App — Frontend

| Package | Purpose |
|---------|---------|
| `react` 18 | UI library |
| `vite` | Build tool |
| `typescript` | Type safety |
| `@tanstack/react-query` | Server state management |
| `react-router-dom` v6 | Client-side routing |
| `tailwindcss` | Utility CSS framework |
| `@radix-ui/*` | Accessible UI primitives |
| `recharts` | Charts and graphs |
| `axios` | HTTP client |
| `lucide-react` | Icon library |

---

### Documentation Map

| File | Contents |
|------|---------|
| `docs/USER_GUIDE.md` | **This file** — complete guide for end users and developers |
| `docs/CHANGELOG.md` | Version history |
| `docs/WEB_APP_PLAN.md` | Full web app transformation plan (phases, API design, DB schema) |
| `docs/PROJECT_SUMMARY.md` | Project summary and architecture overview |
| `README.md` | GitHub repository overview and quick start |
