# Testing Guide

How to test the web scraper application and verify it's working correctly.

---

## Quick Start

### Run Everything
```powershell
cd "C:\Users\Andres\OneDrive\Python Projects\webscrapper"
python main.py
```

### Verify Results
```powershell
cd tests
python verify_datacamp_db.py
```

---

## Available Test Scripts

### Location: `tests/` folder

All test and verification scripts are organized in the tests folder.

#### Test Scripts (Unit & Integration)
```
tests/
├── test_scraper.py              # Test scraper base class
├── test_analyzer.py             # Test text analysis
├── test_models_sync.py          # Test database models
├── test_main_workflow.py        # Test full workflow
├── test_realpython_rules.py     # Test Real Python extraction
├── test_datacamp_extraction.py  # Test DataCamp extraction
├── test_freecodecamp_scraper_new.py
└── test_datacamp_scraper_new.py
```

#### Verification Scripts
```
tests/
├── verify_datacamp_db.py        # Verify DataCamp articles in database
├── check_db.py                  # Quick database check
├── show_results.py              # Display all results
├── final_verification.py        # Comprehensive verification
└── verify_scrape.py             # Detailed article listing
```

---

## Running Tests

### Option 1: Run All Unit Tests
```powershell
cd tests
pytest -v
```

Output shows:
- ✅ Passed tests
- ❌ Failed tests
- ⏭️  Skipped tests
- Total count and time

### Option 2: Run Specific Test File
```powershell
cd tests
pytest test_scraper.py -v
```

### Option 3: Run Specific Test
```powershell
cd tests
pytest test_scraper.py::test_name -v
```

### Option 4: Run with Coverage
```powershell
cd tests
pytest --cov=webscraper_core
```

---

## Verification Scripts

### Quick Database Check (1 second)
```powershell
cd tests
python check_db.py
```

Shows:
- Total articles in database
- Count by source
- Quick status summary

**Use when**: You just want a quick verification

---

### Detailed Article List (2 seconds)
```powershell
cd tests
python verify_scrape.py
```

Shows:
- Formatted table of all articles
- Title, Author, URL, Date
- Article count

**Use when**: You want to see specific articles

---

### Complete Results Display (3 seconds)
```powershell
cd tests
python show_results.py
```

Shows:
- Summary statistics
- Articles by source
- Full article details
- Database status

**Use when**: You want comprehensive overview

---

### Comprehensive Verification (5-10 seconds)
```powershell
cd tests
python final_verification.py
```

Performs:
- ✅ Database connection check
- ✅ Table structure verification
- ✅ Article count validation
- ✅ Live extraction test
- ✅ Data integrity check

**Use when**: You want full system verification

---

### DataCamp Extraction Test
```powershell
cd tests
python test_datacamp_extraction.py
```

Performs:
- 🌐 Fetches DataCamp blog
- 📊 Extracts articles
- 💾 Displays results
- 📁 Saves to JSON file

**Use when**: Testing DataCamp scraper specifically

---

### Real Python Rules Test
```powershell
cd tests
python test_realpython_rules.py
```

Verifies:
- ✅ Real Python extraction rules work
- ✅ All required fields present
- ✅ Date parsing correct

**Use when**: Checking Real Python extraction

---

## Typical Testing Workflow

### After First Installation
```powershell
# 1. Run the scraper
python main.py

# 2. Verify it worked
cd tests
python check_db.py

# 3. See the results
python show_results.py
```

### After Making Changes
```powershell
# 1. Run tests for changed component
cd tests
pytest test_models_sync.py -v

# 2. Run full verification
python final_verification.py

# 3. Run main to check end-to-end
cd ..
python main.py
```

### Complete Verification Suite
```powershell
cd tests

# Unit tests
pytest -v

# Verification tests
python check_db.py
python verify_scrape.py
python show_results.py
python final_verification.py

# Specific scraper tests
python test_datacamp_extraction.py
python test_realpython_rules.py
```

---

## Test Categories

### Unit Tests
Test individual components in isolation:
- `test_scraper.py` - Scraper class methods
- `test_analyzer.py` - Text analysis functions
- `test_models_sync.py` - Model creation and relationships

### Integration Tests
Test components working together:
- `test_main_workflow.py` - Full workflow end-to-end
- `test_models_sync.py` - Database integration
- Verification scripts

### Source-Specific Tests
Test each data source:
- `test_datacamp_extraction.py` - DataCamp blog
- `test_realpython_rules.py` - Real Python
- `test_freecodecamp_scraper_new.py` - FreeCodeCamp

---

## Expected Results

### Successful Scraper Run
```
✅ DataCamp: 17 articles created
✅ Real Python: 19 articles (from cache)
✅ FreeCodeCamp: 25 articles (from cache)
✅ Total: 61 articles
✅ Success Rate: 100%
```

### Successful Database Verification
```
✅ Database Connection: OK
✅ Tables Created: OK
✅ Total Articles: 61
✅ DataCamp Articles: 17
✅ Deduplication: Working
✅ All Checks: PASSED
```

---

## Troubleshooting Tests

### Test Failed: Database Connection
```
Problem: "Can't connect to database"
Solution:
1. Verify scraper_data.db exists
2. Run: python main.py (to create if missing)
3. Check file permissions
```

### Test Failed: No Articles Found
```
Problem: "Expected 17 articles, found 0"
Solution:
1. Run: python main.py (to scrape)
2. Wait for completion
3. Run test again
```

### Test Failed: Extraction Rules Changed
```
Problem: "Article title not found"
Solution:
1. Check website HTML structure
2. Update scraper class
3. Update EXTRACTION_RULES.md
4. Run tests again
```

### Test Failed: Network Error
```
Problem: "Failed to fetch URL"
Solution:
1. Check internet connection
2. Verify website is accessible
3. Try running individually
4. Check for rate limiting
```

---

## Test Metrics

### Coverage Goals
- Unit test coverage: > 80%
- Integration test coverage: > 70%
- Overall: > 75%

### Performance Targets
- Individual test: < 1 second
- Full test suite: < 30 seconds
- Main scraper run: < 60 seconds

### Quality Metrics
- Success rate: > 95%
- Deduplication accuracy: 100%
- Date parsing success: > 90%

---

## CI/CD Integration

### Running in Automation
```powershell
# For automated testing
cd tests
pytest -v --tb=short

# For automated verification
python final_verification.py
```

Exit codes:
- 0 = All tests passed ✅
- 1 = Some tests failed ❌

---

## Debugging

### Enable Debug Output
```python
# In tests/test_file.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print Statements
```python
# In test code
print(f"DEBUG: article_count = {len(articles)}")
```

### Use Debugger
```powershell
# Run with debugger
python -m pdb tests/verify_datacamp_db.py
```

---

## Best Practices

✅ **Do**
- Run tests after changes
- Use verification scripts for manual checks
- Keep test output clean and readable
- Document test failures

❌ **Don't**
- Skip tests to save time
- Leave debug prints in production code
- Ignore test failures
- Change test logic instead of fixing code

---

## Maintenance

### Regular Testing Schedule
- After each code change: Run affected tests
- Before deployment: Run full test suite
- Daily: Run verification scripts
- Weekly: Full system test

### Updating Tests
When adding new scraper:
1. Create test file: `test_newsource.py`
2. Add to pytest discovery
3. Run: `pytest test_newsource.py -v`
4. Update verification scripts

---

**Status**: All tests passing  
**Last Updated**: October 18, 2025  
**Ready for**: Production use
