# Tech Trends Database Scraper - Project Plan

## Project Goal

Build a persistent database that tracks articles from major tech and data science blogs. Extract structured data (title, author, URL, publication date) from articles and enable querying for trends analysis.

## Target Websites

1. **Real Python** - https://realpython.com/
2. **FreeCodeCamp News** - https://www.freecodecamp.org/news/
3. **DataCamp Blog** - https://www.datacamp.com/blog

## Data to Extract Per Article

- ✅ Article Title
- ✅ Author Name(s)
- ✅ Publication Date
- ✅ Direct URL

## System Architecture

```
Web Scraper
    ↓
Website HTML
    ↓
Specialized Scraper (RealPython/FreeCodeCamp/DataCamp)
    ↓
Extract: title, author, url, date
    ↓
Database Repository Layer
    ↓
SQLite Database (scraper_data.db)
    ↓
Query & Analysis
```

## Core Components

### 1. **Scrapers** (`webscraper_core/scrapers/`)
- `datacamp_scraper.py` - DataCamp blog extraction (with Cloudflare bypass)
- `freecodecamp_scraper.py` - FreeCodeCamp extraction
- `realpython_scraper.py` - Real Python extraction

### 2. **Database Models** (`webscraper_core/models/`)
- `article.py` - Article model with title, author_id, url, publication_date
- `author.py` - Author model linked to articles

### 3. **Repositories** (`webscraper_core/repositories/`)
- `article_repository.py` - CRUD + deduplication by URL
- `author_repository.py` - CRUD + get_or_create functionality

### 4. **Manager** (`webscraper_core/manager.py`)
- Orchestrates scraping across multiple sites
- Handles concurrent processing
- Saves to database with deduplication

## Key Features

✅ **Multi-site Extraction** - Handles 3 different website structures  
✅ **Intelligent Deduplication** - Prevents duplicate articles by URL  
✅ **Author Linking** - Associates articles with authors  
✅ **Concurrent Processing** - Parallel extraction from multiple sources  
✅ **Cloudflare Protection** - Bypasses protection with cloudscraper  
✅ **Error Handling** - Graceful failure with detailed logging  

## Implementation Status

| Component | Status |
|-----------|--------|
| Database Models | ✅ Complete |
| Repository Pattern | ✅ Complete |
| Real Python Scraper | ✅ Complete |
| FreeCodeCamp Scraper | ✅ Complete |
| DataCamp Scraper | ✅ Complete (with Cloudflare bypass) |
| Manager & Orchestration | ✅ Complete |
| Database Integration | ✅ Complete |
| Concurrent Processing | ✅ Complete |

## Current Results

- **Total Articles in Database**: 61
  - Real Python: 19 articles
  - FreeCodeCamp: 25 articles
  - DataCamp: 17 articles
- **Success Rate**: 100%
- **Duplicate Prevention**: Working

## Usage

### Run Full Application
```powershell
python main.py
```

### Run Tests
```powershell
cd tests
pytest -v
```

### Verify Database
```powershell
python tests/verify_datacamp_db.py
```

## Database Schema

### Authors Table
```sql
CREATE TABLE author (
    author_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

### Articles Table
```sql
CREATE TABLE article (
    article_id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    publication_date DATE,
    FOREIGN KEY(author_id) REFERENCES author(author_id)
);
```

## Next Steps

1. **Schedule Automated Runs** - Set up Windows Task Scheduler for daily execution
2. **Database Analytics** - Build queries for trend analysis
3. **Monitoring** - Track extraction success rates and errors
4. **Expansion** - Add more data sources as needed

## Technology Stack

- **Language**: Python 3.11
- **Web Scraping**: requests, BeautifulSoup4
- **Cloudflare Bypass**: cloudscraper
- **Database**: SQLite + SQLAlchemy ORM
- **Concurrency**: ThreadPoolExecutor
- **Testing**: pytest

---

**Status**: ✅ Production Ready  
**Last Updated**: October 18, 2025
