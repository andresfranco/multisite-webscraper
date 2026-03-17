# Multisite Web Scraper

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Docker](https://img.shields.io/badge/docker-compose-blue)

A web scraping platform with two usage modes:

- **CLI tool** — scrape Real Python, FreeCodeCamp, and DataCamp from a single command. Results stored in SQLite. No infrastructure required.
- **Web app** — full-stack application with a React UI, FastAPI backend, Celery workers, PostgreSQL, and Redis. Scrape any website using configurable CSS/XPath selectors, monitor jobs in real time, and export results in JSON, CSV, or Excel.

---

## Documentation

All detailed documentation lives in the [`docs/`](docs/) folder:

| File | Description |
|------|-------------|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **Complete guide** — setup, CLI reference, web app walkthrough, API reference, scrape config format, scheduling, exports, troubleshooting |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Architecture overview, design patterns, folder structure, and known limitations |
| [docs/WEB_APP_PLAN.md](docs/WEB_APP_PLAN.md) | Full web app design — universal scraping engine, database schema, API design, implementation roadmap |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Version history and release notes |

**Start here:**
- New to the project → [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Want to understand the architecture → [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- Running the web app → [Web App section below](#web-app)

---

## Quick Start

### CLI Tool

No Docker or database server required.

```bash
git clone https://github.com/andresfranco/multisite-webscraper.git
cd multisite-webscraper
pip install requests beautifulsoup4 sqlalchemy cloudscraper pytest

# Scrape all three default sites
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog

# Options
python main.py --urls https://realpython.com/ --workers 3 --mode debug
python main.py --help
```

Results are saved to `scraper_data.db` (SQLite, created automatically).

**CLI options:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--urls URL [URL ...]` | required | One or more URLs to scrape |
| `--workers N` | `5` | Number of concurrent threads |
| `--mode normal\|debug` | `normal` | Output verbosity |

See [docs/USER_GUIDE.md — CLI section](docs/USER_GUIDE.md#part-1--cli-scraper-production-ready) for full reference.

---

### Web App

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# Start all services (API, worker, beat scheduler, PostgreSQL, Redis)
docker compose up -d

# Run database migrations (first time only)
docker compose exec api alembic upgrade head

# View logs
docker compose logs -f
```

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:5173 |
| API (Swagger docs) | http://localhost:8000/docs |

**First login:** There are no default credentials. Register a new account at http://localhost:5173/register or via the API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "myuser", "password": "mypassword"}'
```

Stop everything:
```bash
docker compose down
```

See [docs/USER_GUIDE.md — Web App section](docs/USER_GUIDE.md#part-2--web-app-in-progress) for full setup, configuration, and usage instructions.

---

## Project Layout

```
multisite-webscraper/
├── main.py                     # CLI entry point
├── webscraper_core/            # CLI scraper package
│   ├── manager.py              # Orchestration and concurrency
│   ├── scraper.py              # Base WebScraper class
│   ├── scrapers/               # Site-specific extractors
│   ├── models/                 # SQLAlchemy ORM models
│   ├── repositories/           # Data access layer
│   └── database.py             # SQLite session factory
├── backend/                    # FastAPI web app
│   ├── app/
│   │   ├── main.py             # FastAPI app factory
│   │   ├── api/v1/             # REST API routes
│   │   ├── core/scraping/      # Universal scraping engine
│   │   ├── models/             # SQLAlchemy async models
│   │   └── schemas/            # Pydantic request/response schemas
│   ├── celery_app.py           # Celery worker and beat configuration
│   ├── alembic/                # Database migrations
│   └── Dockerfile
├── frontend/                   # React + Vite frontend
│   └── src/
│       ├── pages/              # Dashboard, Configs, Jobs, Results, Schedules
│       └── api/                # Typed API client wrappers
├── docker-compose.yml          # Development stack
├── docs/                       # All documentation
└── tests/                      # CLI test suite (32 tests)
```

---

## Features

### CLI
- Scrapes Real Python, FreeCodeCamp, and DataCamp
- Concurrent processing with configurable worker threads
- URL-based deduplication
- SQLite storage via SQLAlchemy ORM
- Debug mode

### Web App
- Scrape **any website** using configurable CSS/XPath selectors
- Auto-detection of selectors from a URL
- Headless browser support (Playwright) for JavaScript-rendered pages
- Pagination support: next-link, page parameter
- Real-time job progress via WebSocket
- Scheduled scraping with cron expressions (Celery Beat)
- Export results as JSON, CSV, or Excel
- JWT authentication and API key support
- robots.txt compliance and configurable rate limiting

---

## Testing

```bash
# CLI unit and functional tests (32 tests)
pytest tests/ -v

# Backend API tests
cd backend && pytest tests/ -v

# Frontend component tests
cd frontend && npm test

# CLI database verification scripts
python tests/check_db.py           # record counts (~1s)
python tests/verify_scrape.py      # list extracted articles (~2s)
python tests/final_verification.py # full data integrity check (~10s)
```

---

## Stack

**CLI:** Python 3.12+ · BeautifulSoup4 · SQLAlchemy 2.0 · SQLite · cloudscraper · pytest

**Backend:** Python 3.11+ · FastAPI 0.115 · SQLAlchemy 2.0 async · PostgreSQL 16 · Celery 5.4 · Redis 7 · Playwright · httpx · Alembic · structlog

**Frontend:** React 18 · TypeScript · Vite · TanStack Query · React Router v6 · Tailwind CSS · Radix UI · Recharts · Axios

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CLI: no articles extracted | Check internet access, run `--mode debug`, verify the URL opens in a browser |
| CLI: import errors | `pip install requests beautifulsoup4 sqlalchemy cloudscraper` |
| CLI: database errors | Delete `scraper_data.db` and re-run |
| Web app: port already in use | Check ports 8000, 5432, 6379 with `netstat -ano \| findstr :<port>` |
| Web app: job stays pending | Ensure the worker container is running (`docker compose ps`) |
| Web app: 401 Unauthorized | JWT token expired — log in again |
| Web app: Playwright errors | Run `docker compose exec api playwright install chromium` |

For more detail see [docs/USER_GUIDE.md — Troubleshooting](docs/USER_GUIDE.md#troubleshooting-web-app).

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for any new behaviour
4. Run `pytest tests/ -v` and confirm all tests pass
5. Submit a pull request

---

MIT License · [Andres Franco](https://github.com/andresfranco)
