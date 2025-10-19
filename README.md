# Multisite Web Scraper

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)

Production-ready web scraper for multiple tech websites. Extracts articles with CLI control and SQLite storage.

**Status**: 61 articles ✅ | 32/32 tests ✅ | CLI ready ✅

---

## Quick Start

### Install
```bash
git clone https://github.com/andresfranco/multisite-webscraper.git
cd multisite-webscraper
pip install requests beautifulsoup4 sqlalchemy cloudscraper pytest
```

### Run
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog
python main.py --urls https://realpython.com/ --workers 3 --mode debug
python main.py --help
```

---

## What It Does

Extracts article metadata from 3 tech sites:

| Site | Articles |
|------|----------|
| Real Python | 19 |
| FreeCodeCamp | 25 |
| DataCamp | 17 |

Each article: Title, Author(s), Date, URL

---

## CLI Options

```
--urls URL [URL ...]      Required. URLs to scrape
--workers N               Optional. Threads (default: 5)
--mode normal|debug       Optional. Verbosity (default: normal)
```

See [docs/06_CLI_INTERFACE.md](docs/06_CLI_INTERFACE.md) for examples.

---

## Project Layout

```
main.py                 # Entry point
webscraper_core/        # Core logic
  scrapers/            # Site-specific extractors
  models/              # ORM models
  repositories/        # Data access
tests/                 # 32 tests (all passing)
docs/                  # 15 docs
```

---

## Features

- ✅ Multi-site support (Real Python, FreeCodeCamp, DataCamp)
- ✅ Concurrent processing (configurable workers)
- ✅ Smart deduplication by URL
- ✅ SQLite database
- ✅ Full CLI with validation
- ✅ Debug mode
- ✅ 32/32 tests passing

---

## Architecture

**Patterns Used**:
- Repository Pattern - Data access
- Factory Pattern - Scraper selection by URL
- Specialist Pattern - Site-specific extractors
- Session Sharing - Single DB session across workers

See [docs/01_PROJECT_PLAN.md](docs/01_PROJECT_PLAN.md)

---

## Testing

```bash
pytest tests/ -v                  # All tests
pytest tests/test_scraper.py -v   # Specific
cd tests && python verify_scrape.py  # Verify extraction
```

**Results**: 32/32 passing
- 23 unit tests
- 9 functional CLI tests

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No articles | Check internet, verify URLs, run `--mode debug` |
| DB errors | Delete `scraper_data.db` and re-run |
| Import errors | `pip install -r requirements.txt` |
| Overload | Use `--workers 2` |

---

## Documentation

**Start Here**:
- [00_GETTING_STARTED.md](docs/00_GETTING_STARTED.md) - Setup & basics
- [06_CLI_INTERFACE.md](docs/06_CLI_INTERFACE.md) - CLI reference

**For Developers**:
- [01_PROJECT_PLAN.md](docs/01_PROJECT_PLAN.md) - Architecture
- [03_IMPLEMENTATION.md](docs/03_IMPLEMENTATION.md) - How it works
- [04_TESTING.md](docs/04_TESTING.md) - Testing

**Reference**:
- [CHANGELOG.md](docs/CHANGELOG.md) - History
- [ARCHIVE.md](docs/ARCHIVE.md) - Technical specs

---

## Stack

Python 3.12+ | BeautifulSoup4 | SQLAlchemy 2.0+ | SQLite | pytest | ThreadPoolExecutor

---

## Contributing

1. Fork repo
2. Create feature branch
3. Add tests
4. Run `pytest tests/ -v`
5. Submit PR

---

MIT License • [Andres Franco](https://github.com/andresfranco) • October 2025
