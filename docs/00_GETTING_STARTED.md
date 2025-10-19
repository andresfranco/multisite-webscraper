# Getting Started with Tech Trends Database Web Scraper

**Last Updated**: October 19, 2025  
**Status**: Production Ready

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/andresfranco/multisite-webscraper.git
cd multisite-webscraper

# Install dependencies
pip install requests beautifulsoup4 sqlalchemy cloudscraper pytest
```

### Running the Scraper

#### Basic Usage (with default settings)
```bash
# Scrape all three websites with 5 worker threads
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog
```

#### Single Website
```bash
python main.py --urls https://realpython.com/
```

#### Multiple Websites with Custom Workers
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news --workers 3
```

#### Debug Mode for Troubleshooting
```bash
python main.py --urls https://realpython.com/ --mode debug
```

#### View All Options
```bash
python main.py --help
```

### Verify Results

```bash
# Quick database check
cd tests
python check_db.py

# View all extracted articles
python verify_scrape.py

# Comprehensive verification
python final_verification.py
```

### Run Tests
```bash
cd tests
pytest -v                              # All tests
pytest test_scraper.py -v             # Specific test
```

---

## Project Structure

```
multisite-webscraper/
├── main.py                           # Entry point with CLI interface
├── README.md                         # GitHub repository guide
├── .gitignore                        # Git ignore rules
├── scraper_data.db                   # SQLite database (generated)
│
├── webscraper_core/                  # Core scraper package
│   ├── manager.py                    # Orchestration & concurrency
│   ├── scraper.py                    # Base WebScraper class
│   ├── database.py                   # SQLAlchemy setup
│   ├── analyzer.py                   # Text analysis
│   │
│   ├── models/                       # ORM models
│   │   ├── base.py                   # Declarative base
│   │   ├── article.py                # Article model
│   │   └── author.py                 # Author model
│   │
│   ├── repositories/                 # Repository pattern
│   │   ├── base_repository.py        # Base repository
│   │   ├── article_repository.py     # Article operations
│   │   └── author_repository.py      # Author operations
│   │
│   └── scrapers/                     # Specialized scrapers
│       ├── realpython_scraper.py     # Real Python scraper
│       ├── freecodecamp_scraper.py   # FreeCodeCamp scraper
│       └── datacamp_scraper.py       # DataCamp scraper
│
├── tests/                            # Test suite
│   ├── test_scraper.py               # Scraper unit tests
│   ├── test_analyzer.py              # Analyzer tests
│   ├── test_main_workflow.py         # Integration tests
│   ├── check_db.py                   # Database verification
│   ├── verify_scrape.py              # Article verification
│   └── final_verification.py         # Comprehensive check
│
└── docs/                             # Documentation
    ├── 00_GETTING_STARTED.md         # Quick start guide (this file)
    ├── 01_PROJECT_PLAN.md            # Project goals & architecture
    ├── 02_EXTRACTION_RULES.md        # HTML extraction overview
    ├── 03_IMPLEMENTATION.md          # How it works
    ├── 04_TESTING.md                 # Testing procedures
    ├── 06_CLI_INTERFACE.md           # CLI documentation
    ├── CHANGELOG.md                  # Tracking changes
    ├── DATA_CAMP_RULES.md            # DataCamp extraction rules
    ├── FREE_CODE_CAMP_RULES.md       # FreeCodeCamp extraction rules
    └── REAL_PYTHON_RULES.md          # Real Python extraction rules
```

---

## Key Features

✅ **Multi-site Extraction** - Handles 3 different website structures  
✅ **CLI Interface** - Full command-line control with `--urls`, `--workers`, `--mode`  
✅ **Intelligent Deduplication** - Prevents duplicate articles  
✅ **Concurrent Processing** - Parallel extraction with configurable workers  
✅ **Database Storage** - SQLite with proper relationships  
✅ **Error Handling** - Graceful failures with logging  
✅ **Debug Mode** - Verbose logging for troubleshooting  
✅ **Comprehensive Tests** - 23+ tests all passing  

---

## What It Extracts

From each website, the scraper captures:
- **Article Title**
- **Author(s)**
- **Publication Date**
- **Direct URL**

Currently supported websites:
- **Real Python** (19 articles) - https://realpython.com/
- **FreeCodeCamp** (25 articles) - https://www.freecodecamp.org/news/
- **DataCamp** (17 articles) - https://www.datacamp.com/blog

---

## Next Steps

1. **Learn the CLI**: Read [06_CLI_INTERFACE.md](06_CLI_INTERFACE.md)
2. **Understand Architecture**: Read [01_PROJECT_PLAN.md](01_PROJECT_PLAN.md)
3. **See Implementation**: Read [03_IMPLEMENTATION.md](03_IMPLEMENTATION.md)
4. **Run Tests**: Follow [04_TESTING.md](04_TESTING.md)
5. **Check Changes**: See [CHANGELOG.md](CHANGELOG.md)

---

## Performance Tips

- **Fewer workers (1-3)**: Lower resource usage, slower scraping
- **Default (5)**: Balanced performance and resource usage
- **More workers (6-10)**: Higher resource usage, faster scraping

---

## Troubleshooting

### No articles extracted?
1. Check internet connection
2. Verify URLs are accessible
3. Run with `--mode debug` for more information
4. Check if websites are blocking the scraper

### Database errors?
1. Delete `scraper_data.db` to reset
2. Run the scraper again to recreate

### Import errors?
```bash
# Install/reinstall dependencies
pip install -r requirements.txt
```

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| [00_GETTING_STARTED.md](00_GETTING_STARTED.md) | This guide - quick start |
| [01_PROJECT_PLAN.md](01_PROJECT_PLAN.md) | Project goals & design |
| [03_IMPLEMENTATION.md](03_IMPLEMENTATION.md) | How the system works |
| [06_CLI_INTERFACE.md](06_CLI_INTERFACE.md) | CLI reference |
| [04_TESTING.md](04_TESTING.md) | Testing guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history & changes |

---

See [../README.md](../README.md) for the main GitHub repository overview.
