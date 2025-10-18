# Tests & Verification Guide# Tests Documentation



This folder contains all test scripts and verification utilities for the Real Python Web Scraper.This folder contains test scripts that verify the functionality and integration of the `webscraper_core` modules.



## 📋 Folder Contents## Project Structure



``````

tests/webscrapper/

├── __init__.py├── webscraper_core/           # Core scraper package

├── README.md (this file)│   ├── __init__.py

││   ├── database.py            # SQLAlchemy setup

├── Unit Tests:│   ├── manager.py             # Orchestration logic

│   ├── test_scraper.py              # WebScraper unit tests│   ├── scraper.py             # HTML fetching & extraction

│   ├── test_analyzer.py             # Text analyzer tests│   ├── analyzer.py            # Text analysis

│   ├── test_article_extraction.py   # Article extraction tests│   ├── models/                # ORM models

│   └── test_call_packages.py        # Package dependency tests│   │   ├── __init__.py

││   │   ├── base.py            # Shared declarative base

├── Integration Tests:│   │   ├── author.py          # Author model

│   ├── test_models_sync.py          # Database models integration│   │   └── article.py         # Article model

│   └── test_main_workflow.py        # Complete workflow tests│   └── repositories/          # Repository pattern

││       ├── __init__.py

└── Verification Scripts:│       ├── base_repository.py # Generic base repository

    ├── check_db.py                  # Quick database check│       ├── author_repository.py

    ├── verify_scrape.py             # Detailed article list│       └── article_repository.py

    ├── show_results.py              # Complete demonstration│

    ├── final_verification.py        # Comprehensive verification├── tests/                     # Test suite

    └── test_realpython_rules.py     # Real Python rules compliance│   ├── __init__.py

```│   ├── test_scraper.py        # WebScraper unit tests

│   ├── test_analyzer.py       # Analyzer unit tests

## 🚀 Quick Start│   ├── test_models_sync.py    # Integration tests

│   └── README.md              # This file

### Run All Tests│

```bash├── main.py                    # Entry point

cd tests├── debug_analyzer.py          # Debug utilities

pytest . -v├── scraper_data.db            # Production database

```└── check_database_records.py  # Database query utility

```

### Run Verification (Choose One)

```bash## Test Files

python check_db.py                  # Quick check (1 sec)

python verify_scrape.py             # Article list (2 sec)### 1. `test_scraper.py`

python show_results.py              # Full demo (3 sec)**Purpose**: Verify the WebScraper class correctly fetches and extracts titles from HTML content.

python final_verification.py        # Comprehensive (5-10 sec)

```**What it tests**:

- WebScraper initialization

---- Title extraction from HTML (h1, h2, h3 tags)

- Handling empty HTML documents

## 📝 Unit Tests- Custom HTML input via `scrape(response_text=...)`

- Proper list return type from extraction methods

### 1. `test_scraper.py`

**Purpose**: Test WebScraper HTML parsing and article extraction**How to run**:

```bash

**Tests**:python tests/test_scraper.py

- ✓ `test_extract_article_data_empty` - Handles empty HTML```

- ✓ `test_extract_article_data_with_articles` - Extracts real articles

- ✓ `test_extract_article_data_structure` - Validates structure**Expected output**:

- ✓ `test_scrape_returns_article_list` - Return type verification```

- ✓ `test_extract_titles_backward_compatibility` - Legacy supportRunning scraper tests...



**Run**:✓ WebScraper initializes correctly

```bash✓ extract_titles returns empty list for empty HTML

pytest test_scraper.py -v✓ extract_titles extracts all titles correctly

```✓ scrape method works with custom HTML



**What it validates**:✅ All scraper tests passed!

- Real Python HTML selector correctness```

- Article data extraction accuracy

- Error handling for edge cases**What it validates**:

- ✅ WebScraper class initializes without errors

---- ✅ Titles are correctly extracted from HTML elements

- ✅ Edge cases (empty HTML) handled gracefully

### 2. `test_analyzer.py`- ✅ Custom HTML input works as expected

**Purpose**: Test text analysis and word frequency

---

**Tests**:

- Punctuation removal### 2. `test_analyzer.py`

- Contraction expansion**Purpose**: Verify the text analyzer correctly processes titles, removes punctuation, handles contractions, and counts word frequencies.

- Stop word filtering

- Word frequency counting**What it tests**:

- Basic title processing and text generation

**Run**:- Punctuation removal and contraction expansion ("what's" → "what is")

```bash- Stop word filtering ("the", "and", "or", etc.)

pytest test_analyzer.py -v- Word frequency counting via Counter

```- Edge cases (empty input)



---**How to run**:

```bash

### 3. `test_article_extraction.py`python tests/test_analyzer.py

**Purpose**: Test article extraction from different sources```



**Run**:**Expected output**:

```bash```

pytest test_article_extraction.py -vRunning analyzer tests...

```

✓ process_titles returns text and counter

---✓ Punctuation and contractions handled correctly

✓ Stop words are filtered correctly

## 🔧 Integration Tests✓ Counter tracks word frequencies accurately

✓ Empty titles handled gracefully

### 4. `test_models_sync.py`

**Purpose**: Test database models and relationships✅ All analyzer tests passed!

```

**Validates**:

- Database initialization**What it validates**:

- Author-Article relationships- ✅ Text preprocessing removes punctuation correctly

- Repository CRUD operations- ✅ Contractions are expanded properly

- ✅ Stop words are filtered when provided

**Run**:- ✅ Counter object tracks frequencies accurately

```bash- ✅ Empty input doesn't cause errors

pytest test_models_sync.py -v

```---



---### 3. `test_models_sync.py`

**Purpose**: Integration test verifying that the Author and Article models, repositories, and database layers work together properly.

### 5. `test_main_workflow.py`

**Purpose**: Test complete scraping workflow**What it tests**:

- Database initialization (SQLAlchemy engine and session creation)

**Validates**:- Table creation via `Base.metadata.create_all(engine)`

- End-to-end scraping- AuthorRepository CRUD operations (create author)

- Database storage- ArticleRepository CRUD operations (create article)

- Deduplication- Relationship between Author and Article models

- Querying and listing records from both repositories

**Run**:

```bash**How to run**:

pytest test_main_workflow.py -v```bash

```python tests/test_models_sync.py

```

---

**Expected output**:

## 🔍 Verification Scripts- "Initializing database..."

- Created author and article entries printed with their ORM representation

### ✅ Quick Database Check- List of all authors and articles in the database

```bash- "Test completed successfully!"

python check_db.py

```**What it validates**:

- ✅ Models import correctly from centralized `models/__init__.py`

**What it shows**:- ✅ Relationships resolve properly (no missing reference errors)

- Total articles in database- ✅ Session management works in repositories

- Total unique authors- ✅ Create, read, and list operations work end-to-end

- Recent articles with details- ✅ Database schema is correctly initialized



**Use when**: You just need a quick confirmation that data exists---



**Output example**:## Running All Tests

```

Total articles in DB: 19To run all tests individually:

Total authors in DB: 8```bash

python tests/test_scraper.py

Recent articles:python tests/test_analyzer.py

  - Polars vs pandas: What's the Difference? (Author ID: 1)python tests/test_models_sync.py

    URL: https://realpython.com/polars-vs-pandas/```

    Date: 2025-10-15

```Or run all tests at once using pytest (if installed):

```bash

---pytest tests/ -v

```

### 📊 Detailed Article Verification

```bashOr with basic Python (runs each test file):

python verify_scrape.py```bash

```python -m pytest tests/

```

**What it shows**:

- Formatted table of all articles---

- Title, author, and publication date

- All article URLs## Test Database

- Success confirmation

- `test_models_sync.py` creates a temporary database file named `test_scraper.db` in the project root

**Use when**: Want to see all scraped articles nicely formatted- This file is safe to delete; it will be recreated on the next test run

- For production databases, use `scraper_data.db` (created by `webscraper_core/database.py`)

**Output example**:

```---

REAL PYTHON ARTICLES SCRAPED AND SAVED

================================================================================## Architecture Overview

Title                                              | Author          | Date

--------------------------------------------------------------------------------The tests validate this flow:

Polars vs pandas: What's the Difference?          | Ian Eyre        | 2025-10-15

How to Use Python: Your First Steps               | Leodanis...     | 2025-10-13```

...database.py (SQLAlchemy ORM setup)

```    ↓

models/ (Author, Article, Base)

---    ↓

repositories/ (AuthorRepository, ArticleRepository)

### 🎯 Complete Results Demonstration    ↓

```bashtest_models_sync.py (verification)

python show_results.py```

```

**Key components tested**:

**What it shows**:1. **Database Layer**: Engine creation, session management

1. Database statistics (articles & authors)2. **Models Layer**: Declarative models, relationships, cascade operations

2. Complete article table (ID, title, author, date)3. **Repository Layer**: CRUD operations abstracted via BaseRepository

3. Full list of article URLs4. **Integration**: End-to-end data flow from DB to ORM to API

4. Articles grouped by author

5. Data validation results---



**Use when**: Need comprehensive overview of everything## Troubleshooting



**Sections**:### "No module named 'webscraper_core'"

- Database SummaryEnsure you run tests from the project root:

- All Scraped Articles```bash

- Article URLscd c:\Users\Andres\OneDrive\Python Projects\webscrapper

- Articles by Authorpython tests/test_scraper.py

- Data Validation```



---The test files automatically handle path resolution with:

```python

### ✨ Final Comprehensive Verificationimport sys

```bashfrom pathlib import Path

python final_verification.pysys.path.insert(0, str(Path(__file__).parent.parent))

``````



**What it shows**:### Import errors in tests

1. Database connection verification- Run tests from the project root directory

2. Data structure validation- Tests use relative path adjustment (no need for PYTHONPATH)

3. Real Python extraction validation- All modules import correctly via `webscraper_core.*`

4. Live scraper test

5. Complete verification summary### Database errors during test

- Delete `test_scraper.db` and re-run the test

**Use when**: Need thorough validation that everything works- Ensure SQLAlchemy is installed: `pip install sqlalchemy`

- Test database is separate from production (`scraper_data.db`)

**Validation checks**:

- ✓ Database connected---

- ✓ Data structure valid

- ✓ All required fields present## Adding New Tests

- ✓ URLs are absolute format

- ✓ Articles from realpython.comTo add new tests:

- ✓ Live scraper functional1. Create a new file `test_your_feature.py` in this folder

2. Follow the naming convention: `test_*.py`

---3. Import necessary modules from `webscraper_core`

4. Document the test in this README

### 🌐 Real Python Rules Compliance

```bashExample template:

python test_realpython_rules.py```python

```"""Test description."""

from webscraper_core.database import create_connection, create_tables

**What it checks**:from webscraper_core.repositories.author_repository import AuthorRepository

- Correct HTML selector usage

- Real Python website structure compliancedef test_feature():

- Article extraction accuracy    # Setup

- HTML element validation    SessionLocal = create_connection('test_db.db')

    create_tables()

**Use when**: Verifying scraper follows Real Python rules    session = SessionLocal()

    

**Validates**:    # Test logic

- `div.card.border-0` elements found    repo = AuthorRepository(session)

- `h2.card-title` elements for titles    # ... assertions ...

- `span.mr-2` elements for dates    

- Proper URL extraction    # Cleanup

    session.close()

---    print("Test passed!")



## 📊 Test Results Summaryif __name__ == '__main__':

    test_feature()

### Expected Results When Everything Works```



✅ **Database**: 19+ articles stored---

✅ **Authors**: 8 unique authors

✅ **Data Integrity**: All fields populated## Best Practices

✅ **URLs**: All absolute format (https://realpython.com/...)

✅ **Dates**: All properly parsed- ✅ Use separate test databases (e.g., `test_*.db`) to avoid affecting production data

✅ **Deduplication**: 0 duplicates on re-run- ✅ Always close sessions after tests: `session.close()`

- ✅ Test one feature per file for clarity

### If Something Fails- ✅ Print informative messages during test execution

- ✅ Document expected behavior in docstrings

| Issue | Solution |

|-------|----------|---

| "Failed to connect to database" | Run: `cd .. && python main.py` |

| "No articles found" | Database needs data - run main scraper |## Related Files

| Import errors | Run from tests folder: `cd tests` |

| Database locked | Delete `scraper_data.db` and retry |- `webscraper_core/database.py` - Core database initialization

- `webscraper_core/models/` - ORM model definitions

---- `webscraper_core/repositories/` - CRUD operation abstractions

- `check_database_records.py` - Utility to query the database (in project root)

## 🔄 Typical Workflows

### First Time Setup
```bash
cd ..
python main.py                      # Scrape articles
cd tests
python check_db.py                  # Quick verify
```

### Verify After Changes
```bash
cd tests
python final_verification.py        # Complete check
pytest test_scraper.py -v          # Run unit tests
```

### Full Test Suite
```bash
cd tests
pytest . -v                         # All tests + coverage
python show_results.py              # Show all results
```

---

## 🎯 Which Script to Use?

| Goal | Script | Command | Time |
|------|--------|---------|------|
| Quick status | `check_db.py` | `python check_db.py` | 1s |
| See articles | `verify_scrape.py` | `python verify_scrape.py` | 2s |
| Full overview | `show_results.py` | `python show_results.py` | 3s |
| Comprehensive | `final_verification.py` | `python final_verification.py` | 5-10s |
| Rules check | `test_realpython_rules.py` | `python test_realpython_rules.py` | 15s |
| Unit tests | pytest | `pytest test_scraper.py -v` | 2-5s |
| All tests | pytest | `pytest . -v` | 10-15s |

---

## 🐛 Debugging Tips

### Enable Detailed Output
```bash
python -c "from webscraper_core.database import create_connection; from webscraper_core.models import Article; s = create_connection('../scraper_data.db')(); print(f'Articles: {s().query(Article).count()}')"
```

### Check Database with sqlite3
```bash
sqlite3 ../scraper_data.db
> SELECT COUNT(*) FROM article;
> SELECT * FROM article LIMIT 5;
> .quit
```

### View Specific Article
```bash
python -c "
from webscraper_core.database import create_connection
from webscraper_core.models import Article
s = create_connection('../scraper_data.db')()
a = s.query(Article).first()
print(f'Title: {a.title}')
print(f'URL: {a.url}')
print(f'Date: {a.publication_date}')
"
```

---

## ✅ Final Verification Checklist

Before considering the project complete:

- [ ] `python check_db.py` - Shows 19+ articles
- [ ] `python verify_scrape.py` - All articles formatted correctly
- [ ] `python show_results.py` - All sections complete
- [ ] `python final_verification.py` - All checks ✓
- [ ] `python test_realpython_rules.py` - Rules compliance ✓
- [ ] `pytest test_scraper.py -v` - All tests pass
- [ ] `pytest . -v` - Full test suite passes

---

## 📚 Related Documentation

- `../README.md` - Main project documentation
- `../docs/REAL_PYTHON_RULES.md` - Official extraction rules
- `../docs/IMPLEMENTATION_SUMMARY.md` - Technical details
- `../COMPLETION_STATUS.md` - Project completion status

---

## 🏆 Status

**✅ PRODUCTION READY**

All verification scripts confirm:
- ✓ 19 Real Python articles extracted
- ✓ All data properly stored in database
- ✓ Scraper follows Real Python rules
- ✓ Complete test coverage
- ✓ Windows compatible
