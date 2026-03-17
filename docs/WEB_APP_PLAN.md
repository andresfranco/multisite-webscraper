# Web Application Transformation Plan

## Goal

Transform the existing CLI-based multisite web scraper into a full-stack web application that can scrape **any website** -- not just the three hardcoded sites -- with a user-friendly UI for configuring scrape jobs, viewing results, and managing extraction rules.

---

## 1. High-Level Architecture

```
                          +-------------------+
                          |   React Frontend  |
                          |   (SPA - Vite)    |
                          +--------+----------+
                                   |
                              REST API / WebSocket
                                   |
                          +--------v----------+
                          |   FastAPI Backend  |
                          |   (Python 3.12+)   |
                          +--------+----------+
                                   |
               +-------------------+-------------------+
               |                   |                   |
     +---------v------+   +-------v--------+   +------v-------+
     |  Scraping       |   |  Job Queue     |   |  Database    |
     |  Engine         |   |  (Celery +     |   |  (PostgreSQL)|
     |  (Universal)    |   |   Redis)       |   |              |
     +--------+--------+   +-------+--------+   +------+-------+
              |                     |                   |
     +--------v--------+           |            +------v-------+
     | Headless Browser |           |            |  Redis       |
     | (Playwright)     |           |            |  (Cache +    |
     +------------------+           |            |   Broker)    |
                                    |            +--------------+
                             +------v-------+
                             | Worker Pool  |
                             | (Celery      |
                             |  Workers)    |
                             +--------------+
```

### Why This Stack

| Choice        | Rationale                                                                 |
|---------------|---------------------------------------------------------------------------|
| **FastAPI**   | Async-native Python, auto-generated OpenAPI docs, WebSocket support, keeps Python scraping core |
| **React**     | Component-based UI, large ecosystem, good for dashboards and real-time updates |
| **PostgreSQL**| Production-grade, handles concurrent access (replaces SQLite limitation), JSON columns for flexible schema |
| **Celery + Redis** | Async job queue for long-running scrape jobs, prevents request timeouts, enables scheduling |
| **Playwright**| Handles JavaScript-rendered pages (SPAs), Cloudflare, dynamic content -- solves the biggest limitation of requests+BS4 |

---

## 2. Universal Scraping Engine Design

The core challenge is making the scraper work with **any website** without writing custom code per site. The solution is a multi-strategy extraction engine.

### 2.1 Extraction Strategies (Priority Order)

```
User submits URL
       |
       v
  1. Check for saved ScrapeConfig for this domain
       |-- YES --> Use saved CSS/XPath selectors
       |-- NO  --> Continue to auto-detection
       v
  2. Auto-Detection Engine
       |
       +-- a. Structural Analysis (find <article>, <h1-h6>, <time>, <a> patterns)
       +-- b. Schema.org / JSON-LD parsing (structured data already on page)
       +-- c. Open Graph / meta tag extraction
       +-- d. RSS/Atom feed detection and parsing
       |
       v
  3. If auto-detection yields low confidence
       |
       +-- Present preview to user
       +-- User refines selectors via visual selector builder
       +-- Save as ScrapeConfig for future runs
```

### 2.2 ScrapeConfig Model

Each site/scrape job is driven by a configuration object:

```python
class ScrapeConfig:
    id: int
    name: str                          # e.g. "Real Python Blog"
    base_url: str                      # e.g. "https://realpython.com/"
    domain: str                        # auto-extracted, e.g. "realpython.com"
    
    # Page fetching
    use_headless_browser: bool         # Playwright vs requests
    wait_for_selector: str | None      # Wait for element before extracting (JS pages)
    custom_headers: dict | None
    
    # Pagination
    pagination_type: str               # "none", "next_link", "scroll", "page_param"
    pagination_selector: str | None    # CSS selector for next page link
    max_pages: int                     # Limit pagination depth
    
    # Item extraction
    item_selector: str                 # CSS selector for each item container (e.g. "article", "div.post-card")
    
    # Field extraction (per item)
    fields: list[FieldConfig]
    
    # Rate limiting
    request_delay_ms: int              # Delay between requests
    concurrent_requests: int           # Max parallel requests for this config
    
    # Scheduling
    schedule_cron: str | None          # e.g. "0 6 * * *" for daily at 6 AM
    is_active: bool
    
    created_at: datetime
    updated_at: datetime

class FieldConfig:
    name: str                          # e.g. "title", "author", "date", "url", "price"
    selector: str                      # CSS selector or XPath
    attribute: str | None              # e.g. "href", "src", "datetime" (None = text content)
    transform: str | None              # e.g. "strip", "parse_date", "to_absolute_url", "regex:(\d+)"
    required: bool
    default_value: str | None
```

### 2.3 What Gets Reused from Current Codebase

| Current Component           | Reuse Strategy                                                     |
|-----------------------------|--------------------------------------------------------------------|
| `WebScraper.fetch_page()`   | Keep as one fetch strategy; add Playwright as second strategy       |
| `_parse_date()`             | Extract into shared utility `utils/date_parser.py`                 |
| `_extract_generic_articles` | Basis for auto-detection heuristics                                |
| Repository pattern          | Evolve into new models but keep the pattern                        |
| `BaseRepository`            | Adapt for PostgreSQL + async (SQLAlchemy async)                    |
| Site-specific scrapers      | Convert into pre-built ScrapeConfig templates                      |
| `analyzer.py`               | Keep as analysis module, expose via API                            |
| `manager.py` orchestration  | Replace with Celery task orchestration                             |

---

## 3. Backend API Design (FastAPI)

### 3.1 API Structure

```
/api/v1/
  |-- /auth/
  |     POST   /register
  |     POST   /login
  |     POST   /refresh
  |
  |-- /configs/
  |     GET    /                    # List all scrape configs
  |     POST   /                    # Create new scrape config
  |     GET    /{id}                # Get config details
  |     PUT    /{id}                # Update config
  |     DELETE /{id}                # Delete config
  |     POST   /{id}/test           # Test config (scrape 1 page, return preview)
  |     POST   /auto-detect         # Auto-detect selectors for a URL
  |
  |-- /jobs/
  |     GET    /                    # List scrape jobs (with filtering/pagination)
  |     POST   /                    # Start a new scrape job (from config)
  |     GET    /{id}                # Get job details + progress
  |     POST   /{id}/cancel         # Cancel a running job
  |     GET    /{id}/logs           # Get job execution logs
  |
  |-- /results/
  |     GET    /                    # List all scraped items (filterable, paginated)
  |     GET    /{id}                # Get single result detail
  |     DELETE /{id}                # Delete a result
  |     GET    /export              # Export results (CSV, JSON, Excel)
  |     GET    /stats               # Aggregated statistics
  |
  |-- /schedules/
  |     GET    /                    # List all scheduled jobs
  |     POST   /                    # Create a schedule
  |     PUT    /{id}                # Update schedule
  |     DELETE /{id}                # Delete schedule
  |
  |-- /ws/
        /jobs/{id}/progress         # WebSocket for real-time job progress
```

### 3.2 Authentication

- JWT-based authentication (access + refresh tokens)
- Optional for single-user deployments (configurable)
- API key support for programmatic access

### 3.3 Key Backend Modules

```
backend/
  |-- app/
  |   |-- main.py                   # FastAPI app, CORS, middleware
  |   |-- config.py                 # Settings (Pydantic BaseSettings)
  |   |-- api/
  |   |   |-- v1/
  |   |       |-- configs.py        # Scrape config endpoints
  |   |       |-- jobs.py           # Job management endpoints
  |   |       |-- results.py        # Results & export endpoints
  |   |       |-- auth.py           # Auth endpoints
  |   |       |-- schedules.py      # Schedule endpoints
  |   |-- core/
  |   |   |-- scraping/
  |   |   |   |-- engine.py         # Universal scraping engine
  |   |   |   |-- fetcher.py        # HTTP + Playwright page fetchers
  |   |   |   |-- extractor.py      # CSS/XPath/auto extraction
  |   |   |   |-- auto_detect.py    # Auto-detect selectors from HTML
  |   |   |   |-- transforms.py     # Field transforms (date, url, strip, regex)
  |   |   |-- tasks/
  |   |   |   |-- scrape_task.py    # Celery task for scraping
  |   |   |   |-- schedule_task.py  # Celery beat scheduled tasks
  |   |-- models/                   # SQLAlchemy models
  |   |-- repositories/             # Data access layer (evolved from current)
  |   |-- schemas/                  # Pydantic request/response schemas
  |   |-- utils/
  |       |-- date_parser.py        # Extracted from current _parse_date()
  |       |-- url_utils.py          # URL normalization
  |       |-- robots.py             # robots.txt checker
  |-- celery_app.py                 # Celery configuration
  |-- alembic/                      # Database migrations
```

---

## 4. Frontend Design (React + Vite)

### 4.1 Pages & Components

| Page                  | Purpose                                                        |
|-----------------------|----------------------------------------------------------------|
| **Dashboard**         | Overview: active jobs, recent results, quick stats             |
| **Scrape Configs**    | List/create/edit scrape configurations                         |
| **Config Builder**    | Visual form to define selectors + live preview                 |
| **Jobs**              | List running/completed/failed jobs with progress bars          |
| **Job Detail**        | Real-time progress via WebSocket, logs, partial results        |
| **Results Browser**   | Table view with filtering, sorting, search across all results  |
| **Result Detail**     | Single scraped item with all fields                            |
| **Export**            | Export filtered results to CSV/JSON/Excel                      |
| **Schedules**         | Manage recurring scrape schedules                              |
| **Settings**          | App configuration, API keys, user profile                      |

### 4.2 Config Builder UX Flow

```
1. User enters a URL
       |
       v
2. System fetches the page and shows a rendered preview (iframe or screenshot)
       |
       v
3. Auto-detection runs and suggests selectors + field mappings
       |
       v
4. User sees a table preview of extracted data
       |
       v
5. User can:
   - Accept the auto-detected config
   - Manually adjust selectors (click elements in preview to generate selectors)
   - Add/remove fields
   - Configure pagination rules
   - Set rate limiting
       |
       v
6. User clicks "Test" to run extraction on 1 page and see results
       |
       v
7. User clicks "Save & Run" to create the config and start a job
```

### 4.3 Frontend Tech

| Library               | Purpose                          |
|-----------------------|----------------------------------|
| React 18+             | UI framework                     |
| Vite                  | Build tool                       |
| TanStack Query        | Server state management          |
| React Router          | Client-side routing              |
| Tailwind CSS          | Styling                          |
| Shadcn/ui             | Component library                |
| Recharts              | Statistics/charts                |
| Monaco Editor         | CSS/XPath selector editor        |

---

## 5. Database Schema (PostgreSQL)

### 5.1 Core Tables

```sql
-- Users (optional, for multi-user deployments)
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key       VARCHAR(64) UNIQUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Scrape configurations (replaces hardcoded scrapers)
CREATE TABLE scrape_configs (
    id                   SERIAL PRIMARY KEY,
    user_id              INT REFERENCES users(id),
    name                 VARCHAR(255) NOT NULL,
    base_url             VARCHAR(2048) NOT NULL,
    domain               VARCHAR(255) NOT NULL,
    use_headless_browser BOOLEAN DEFAULT FALSE,
    wait_for_selector    VARCHAR(500),
    custom_headers       JSONB,
    pagination_type      VARCHAR(20) DEFAULT 'none',
    pagination_selector  VARCHAR(500),
    max_pages            INT DEFAULT 1,
    item_selector        VARCHAR(500) NOT NULL,
    fields               JSONB NOT NULL,          -- Array of FieldConfig objects
    request_delay_ms     INT DEFAULT 1000,
    concurrent_requests  INT DEFAULT 1,
    schedule_cron        VARCHAR(100),
    is_active            BOOLEAN DEFAULT TRUE,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- Scrape jobs (each execution of a config)
CREATE TABLE scrape_jobs (
    id              SERIAL PRIMARY KEY,
    config_id       INT REFERENCES scrape_configs(id) ON DELETE SET NULL,
    user_id         INT REFERENCES users(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
        -- pending, running, completed, failed, cancelled
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    pages_scraped   INT DEFAULT 0,
    items_found     INT DEFAULT 0,
    items_created   INT DEFAULT 0,
    items_skipped   INT DEFAULT 0,
    errors          INT DEFAULT 0,
    error_message   TEXT,
    celery_task_id  VARCHAR(255),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Scraped results (replaces current article + author tables)
CREATE TABLE scraped_items (
    id              SERIAL PRIMARY KEY,
    job_id          INT REFERENCES scrape_jobs(id) ON DELETE CASCADE,
    config_id       INT REFERENCES scrape_configs(id) ON DELETE SET NULL,
    source_url      VARCHAR(2048) NOT NULL,       -- Page URL this item was found on
    item_url        VARCHAR(2048),                 -- Extracted item URL (if applicable)
    data            JSONB NOT NULL,                -- All extracted fields as JSON
    content_hash    VARCHAR(64) UNIQUE,            -- SHA-256 of data for dedup
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Job logs (detailed execution log per job)
CREATE TABLE job_logs (
    id          SERIAL PRIMARY KEY,
    job_id      INT REFERENCES scrape_jobs(id) ON DELETE CASCADE,
    level       VARCHAR(10) NOT NULL,             -- INFO, WARN, ERROR, DEBUG
    message     TEXT NOT NULL,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_scraped_items_config ON scraped_items(config_id);
CREATE INDEX idx_scraped_items_job ON scraped_items(job_id);
CREATE INDEX idx_scraped_items_data ON scraped_items USING GIN(data);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
CREATE INDEX idx_scrape_configs_domain ON scrape_configs(domain);
```

### 5.2 Key Design Decisions

- **JSONB `data` column**: Scraped fields vary per config, so storing them as JSON provides maximum flexibility without schema migrations per scrape target.
- **`content_hash` for dedup**: SHA-256 hash of the serialized extracted data replaces the current URL-only dedup, handling cases where the same content appears at different URLs.
- **GIN index on `data`**: Enables fast filtering/searching within scraped JSON fields.
- **Separation of config vs job vs results**: Allows re-running configs, comparing runs, and tracking history.

### 5.3 Migration from Current Schema

The current `author` and `article` tables map to the new schema as follows:

| Current                | New                                     |
|------------------------|-----------------------------------------|
| `author.name`          | `scraped_items.data->>'author'`         |
| `article.title`        | `scraped_items.data->>'title'`          |
| `article.url`          | `scraped_items.item_url`                |
| `article.publication_date` | `scraped_items.data->>'publication_date'` |
| Hardcoded scraper class | `scrape_configs` row                   |

---

## 6. Real-Time Features

### 6.1 WebSocket Progress Updates

```python
# Backend: FastAPI WebSocket endpoint
@app.websocket("/api/v1/ws/jobs/{job_id}/progress")
async def job_progress(websocket: WebSocket, job_id: int):
    await websocket.accept()
    while True:
        progress = await get_job_progress(job_id)  # From Redis
        await websocket.send_json(progress)
        if progress["status"] in ("completed", "failed", "cancelled"):
            break
        await asyncio.sleep(1)
```

### 6.2 Progress Data Structure

```json
{
    "job_id": 42,
    "status": "running",
    "pages_scraped": 3,
    "pages_total": 10,
    "items_found": 47,
    "items_created": 45,
    "items_skipped": 2,
    "errors": 0,
    "current_url": "https://example.com/page/4",
    "elapsed_seconds": 12,
    "estimated_remaining_seconds": 28
}
```

### 6.3 Implementation

- Celery worker publishes progress to Redis pub/sub after each page
- FastAPI WebSocket endpoint subscribes to Redis channel for that job
- Frontend tracks live progress in the job detail view, currently via the `useJobProgress` polling hook

---

## 7. Security Considerations

| Concern                  | Solution                                                          |
|--------------------------|-------------------------------------------------------------------|
| **Rate limiting**        | Per-config `request_delay_ms`, global rate limiter via Redis      |
| **robots.txt**           | Check and respect `robots.txt` before scraping (configurable)     |
| **User-Agent**           | Configurable, defaults to honest identification                   |
| **SSRF prevention**      | Validate URLs, block private/internal IPs, whitelist protocols    |
| **Input validation**     | Pydantic schemas validate all API inputs                          |
| **SQL injection**        | SQLAlchemy ORM parameterized queries (already in place)           |
| **XSS prevention**      | React auto-escapes, sanitize scraped HTML before display          |
| **Authentication**       | JWT tokens with expiry, bcrypt password hashing                   |
| **API rate limiting**    | FastAPI middleware, Redis-backed rate limiter on API endpoints     |
| **Secrets management**   | Environment variables, never in code or DB                        |
| **CORS**                 | Restrict origins to frontend domain                               |
| **Proxy support**        | Optional proxy rotation for high-volume scraping                  |
| **Legal compliance**     | Terms of service notice, user is responsible for what they scrape |

---

## 8. Scalability Considerations

| Aspect               | Approach                                                            |
|-----------------------|---------------------------------------------------------------------|
| **Concurrent jobs**   | Celery workers scale horizontally; add more workers as needed       |
| **Database**          | PostgreSQL handles concurrent writes; connection pooling via SQLAlchemy |
| **Large result sets** | Paginated API responses, cursor-based pagination for large tables   |
| **JS-heavy sites**    | Playwright runs in worker processes, not blocking the API server    |
| **Storage**           | JSONB keeps schema flexible; archival/cleanup policies for old results |
| **Caching**           | Redis caches config lookups, recent results, rate limit counters    |
| **Monitoring**        | Structured logging (structlog), Prometheus metrics endpoint         |

---

## 9. Technology Recommendations

### Backend
| Package              | Version   | Purpose                                    |
|----------------------|-----------|--------------------------------------------|
| fastapi              | 0.110+    | Web framework                              |
| uvicorn              | 0.27+     | ASGI server                                |
| sqlalchemy[asyncio]  | 2.0+      | Async ORM (evolve from current sync)       |
| alembic              | 1.13+     | Database migrations                        |
| celery               | 5.3+      | Distributed task queue                     |
| redis                | 5.0+      | Broker + cache + pub/sub                   |
| playwright           | 1.41+     | Headless browser for JS-rendered pages     |
| beautifulsoup4       | 4.12+     | HTML parsing (keep from current)           |
| httpx                | 0.27+     | Async HTTP client (replaces requests)      |
| pydantic             | 2.6+      | Data validation                            |
| python-jose          | 3.3+      | JWT handling                               |
| bcrypt               | 4.1+      | Password hashing                           |
| lxml                 | 5.1+      | Fast HTML/XML parser, XPath support        |
| structlog            | 24.1+     | Structured logging                         |

### Frontend
| Package              | Purpose                                    |
|----------------------|--------------------------------------------|
| react                | UI framework                               |
| vite                 | Build tool                                 |
| @tanstack/react-query| Data fetching & caching                   |
| react-router-dom     | Routing                                    |
| tailwindcss          | Utility-first CSS                          |
| shadcn/ui            | Component library                          |
| recharts             | Charts and visualizations                  |
| @monaco-editor/react | Selector editing                           |
| lucide-react         | Icons                                      |

### Infrastructure
| Tool                 | Purpose                                    |
|----------------------|--------------------------------------------|
| Docker + Compose     | Container orchestration for all services   |
| PostgreSQL 16+       | Primary database                           |
| Redis 7+             | Message broker + cache                     |
| Nginx                | Reverse proxy + static file serving        |

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Backend API with existing scraping capabilities exposed via REST

- [ ] Set up project structure (FastAPI + Celery + PostgreSQL + Redis)
- [ ] Create Docker Compose for all services
- [ ] Design and implement new database schema with Alembic migrations
- [ ] Port existing `WebScraper` and site-specific scrapers to new backend
- [ ] Implement `ScrapeConfig` model and CRUD API endpoints
- [ ] Implement `ScrapeJob` model and basic job execution via Celery
- [ ] Implement `ScrapedItem` storage with content-hash dedup
- [ ] Create pre-built ScrapeConfig templates for the 3 existing sites
- [ ] Basic health check and API docs (auto-generated by FastAPI)

**Milestone:** Can create configs and run scrape jobs via API (Swagger UI)

### Phase 2: Universal Scraping Engine (Weeks 3-4)

**Goal:** Scrape any website using configurable selectors

- [ ] Build universal extraction engine with CSS selector + XPath support
- [ ] Implement field transforms (date parsing, URL normalization, regex, strip)
- [ ] Add auto-detection engine (structural analysis, JSON-LD, Open Graph, RSS)
- [ ] Integrate Playwright for JavaScript-rendered pages
- [ ] Add pagination support (next link, scroll, page parameter)
- [ ] Implement robots.txt checking
- [ ] Add configurable rate limiting per domain
- [ ] Test config endpoint (scrape 1 page, return preview without saving)

**Milestone:** Can auto-detect and scrape articles from arbitrary websites via API

### Phase 3: Frontend MVP (Weeks 5-7)

**Goal:** Usable web interface for all core features

- [ ] Set up React + Vite + Tailwind + Shadcn/ui
- [ ] Build Dashboard page (stats overview, recent jobs)
- [ ] Build Scrape Config list and create/edit forms
- [ ] Build Config Builder with live preview (enter URL -> see extracted data)
- [ ] Build Jobs page with status list and progress tracking
- [ ] Build Results Browser with filtering, sorting, and pagination
- [ ] Build Export page (CSV, JSON)
- [ ] Implement WebSocket connection for real-time job progress
- [ ] Error handling and loading states throughout

**Milestone:** Fully functional web application for scraping any website

### Phase 4: Advanced Features (Weeks 8-10)

**Goal:** Production-grade features for reliability and automation

- [ ] Authentication system (JWT login, registration, API keys)
- [ ] Scheduled scraping with Celery Beat (cron expressions)
- [ ] Schedules management UI
- [ ] Visual selector builder (click elements in page preview to generate selectors)
- [ ] Proxy support and rotation
- [ ] Retry logic with exponential backoff
- [ ] Job comparison (diff between runs of same config)
- [ ] Excel export format
- [ ] Structured logging with structlog
- [ ] Error alerting (email/webhook on job failure)

**Milestone:** Production-ready application with scheduling and advanced features

### Phase 5: Polish & Deploy (Weeks 11-12)

**Goal:** Deploy, document, and harden

- [ ] Production Docker configuration (multi-stage builds, security hardening)
- [ ] Nginx reverse proxy configuration
- [ ] Environment-based configuration (dev/staging/prod)
- [ ] API documentation and user guide
- [ ] Comprehensive test suite (backend unit + integration, frontend component tests)
- [ ] Performance testing and optimization
- [ ] Data cleanup/archival policies
- [ ] Monitoring and health checks (Prometheus metrics)
- [ ] Deployment guide (Docker Compose, cloud providers)

**Milestone:** Deployed, documented, and monitored production application

---

## 11. Docker Compose Structure

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis]
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/scraper
      REDIS_URL: redis://redis:6379/0

  worker:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info
    depends_on: [db, redis]

  beat:
    build: ./backend
    command: celery -A celery_app beat --loglevel=info
    depends_on: [redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  db:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: scraper
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

---

## 12. Migration Strategy from Current Codebase

### What to Keep
- `webscraper_core/scraper.py` base class logic -> refactor into `core/scraping/fetcher.py`
- `_parse_date()` utility -> `utils/date_parser.py`
- `_extract_generic_articles()` heuristics -> `core/scraping/auto_detect.py`
- Repository pattern -> evolve for PostgreSQL + async
- Site-specific scraper logic -> convert to ScrapeConfig JSON templates
- `analyzer.py` -> keep as analysis utility, expose via API
- All test patterns -> adapt for new structure

### What to Replace
- `argparse` CLI -> FastAPI REST API + React frontend
- SQLite -> PostgreSQL
- `ThreadPoolExecutor` -> Celery distributed workers
- Global engine/session -> async session factory with proper scoping
- Print statements -> structured logging (structlog)
- Hardcoded scraper factory -> ScrapeConfig-driven universal engine

### Data Migration
- Write a one-time migration script to:
  1. Read all articles from SQLite `scraper_data.db`
  2. Create ScrapeConfig entries for the 3 existing sites
  3. Insert articles as `scraped_items` with proper JSONB data
  4. Generate `content_hash` for each item

---

## Summary

This plan transforms a CLI scraper for 3 hardcoded sites into a full-stack web application that can scrape any website. The key innovations are:

1. **ScrapeConfig-driven extraction** replaces hardcoded scraper classes
2. **Auto-detection engine** reduces manual configuration effort
3. **Playwright integration** handles JavaScript-rendered pages
4. **Celery job queue** enables long-running, scheduled, and concurrent scrape jobs
5. **React dashboard** provides visual configuration, monitoring, and result browsing
6. **PostgreSQL + JSONB** provides flexible storage for varied scraped data schemas

The existing codebase provides a solid foundation -- the repository pattern, scraper base class, and extraction heuristics all carry forward into the new architecture.
