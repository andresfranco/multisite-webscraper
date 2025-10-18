# Implementation Guide

Complete walkthrough of how the web scraper system works and how to maintain it.

---

## System Architecture

### Data Flow
```
1. Website HTML
   ↓
2. Specialized Scraper (with site-specific logic)
   - RealPythonScraper
   - FreeCodeCampScraper  
   - DataCampScraper
   ↓
3. Extract: title, author, url, publication_date
   ↓
4. Manager (orchestration)
   - Concurrent processing
   - Error handling
   ↓
5. Repository Layer
   - Author: get_or_create()
   - Article: add_article_with_dedup()
   ↓
6. SQLite Database
   - Automatic deduplication by URL
   - Author linking
   ↓
7. Query & Analysis
```

---

## Core Components

### 1. Scraper Classes (`webscraper_core/scrapers/`)

#### Base Class: `WebScraper`
```python
class WebScraper:
    def fetch_page(self) -> str
    def extract_article_data(self, html: str) -> List[dict]
```

#### Specialized Scrapers
- **DataCampScraper** - Uses `cloudscraper` to bypass Cloudflare
- **RealPythonScraper** - Handles Real Python structure
- **FreeCodeCampScraper** - Handles FreeCodeCamp structure

Each returns list of article dictionaries:
```python
[
  {
    "title": "Article Title",
    "author": "Author Name",
    "url": "https://example.com/article",
    "publication_date": date(2025, 10, 18)
  },
  ...
]
```

### 2. Database Models (`webscraper_core/models/`)

#### Author Model
```python
class Author(Base):
    author_id: int (PK)
    name: str
    articles: List[Article] (relationship)
```

#### Article Model
```python
class Article(Base):
    article_id: int (PK)
    title: str
    author_id: int (FK)
    url: str (UNIQUE)
    publication_date: date
    author: Author (relationship)
```

### 3. Repository Layer (`webscraper_core/repositories/`)

#### AuthorRepository
```python
def get_or_create(name: str) -> Author
    # Returns existing author or creates new one
```

#### ArticleRepository
```python
def add_article_with_dedup(data: dict, author: Author) -> Optional[Article]
    # Checks if URL exists
    # If new: creates and saves
    # If duplicate: returns None
```

### 4. Manager (`webscraper_core/manager.py`)

Main orchestration logic:

```python
def _process_single(url: str) -> Dict
    # 1. Get appropriate scraper
    # 2. Fetch page content
    # 3. Extract articles
    # 4. Save to database
    # 5. Return statistics

def run_many(urls: List[str]) -> List[Dict]
    # Process multiple URLs concurrently
    # Uses ThreadPoolExecutor with 5 workers

def run_many_and_aggregate(urls: List[str]) -> Tuple[List[Dict], Dict]
    # Run all and return combined statistics
```

---

## How It Works: Step by Step

### Example: Extracting from DataCamp

**Step 1: Scraper Selection**
```python
scraper = DataCampScraper('https://www.datacamp.com/blog')
```

**Step 2: Fetch Page**
```python
html = scraper.fetch_page()  # Uses cloudscraper to bypass Cloudflare
```

**Step 3: Extract Articles**
```python
articles = scraper.extract_article_data(html)
# Returns: [
#   {"title": "...", "author": "...", "url": "...", "publication_date": date(...)},
#   ...
# ]
```

**Step 4: Save to Database**
```python
for article_data in articles:
    author = author_repo.get_or_create(article_data['author'])
    result = article_repo.add_article_with_dedup(article_data, author)
    if result:
        created += 1  # New article
    else:
        skipped += 1  # Duplicate (URL exists)
```

---

## Key Design Patterns

### 1. Repository Pattern
Encapsulates database access logic:
- All DB queries in repository classes
- Clean separation of concerns
- Easy to test and modify

### 2. Factory Pattern
Manager creates appropriate scraper based on URL:
```python
def _get_scraper_for_url(url: str) -> WebScraper:
    if 'realpython.com' in url:
        return RealPythonScraper(url)
    elif 'freecodecamp.org' in url:
        return FreeCodeCampScraper(url)
    elif 'datacamp.com' in url:
        return DataCampScraper(url)
```

### 3. Deduplication by Primary Key
Articles identified uniquely by URL:
```python
existing = article_repo.get_by_url(url)
if existing:
    return None  # Skip duplicate
```

### 4. Concurrent Processing
Multiple sources processed in parallel:
```python
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(_process_single, url): url for url in urls}
    for future in as_completed(futures):
        result = future.result()
```

---

## How to Add New Source

### Step 1: Create Scraper Class
```python
# File: webscraper_core/scrapers/newsource_scraper.py
class NewSourceScraper(WebScraper):
    BASE_URL = 'https://newsource.com'
    
    def fetch_page(self):
        # Custom fetch logic if needed
        return requests.get(self.url).text
    
    def extract_article_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        for article_elem in soup.find_all('article'):
            # Extract title, author, url, date
            article_data = {
                'title': title_text,
                'author': author_text,
                'url': article_url,
                'publication_date': parsed_date
            }
            articles.append(article_data)
        
        return articles
```

### Step 2: Register Scraper in Manager
```python
# In manager.py _get_scraper_for_url()
elif 'newsource.com' in url:
    return NewSourceScraper(url)
```

### Step 3: Add to Target URLs
```python
# In main.py
urls = [
    'https://realpython.com/',
    'https://www.freecodecamp.org/news',
    'https://www.datacamp.com/blog',
    'https://newsource.com'  # Add here
]
```

### Step 4: Test
```powershell
python main.py
python tests/verify_datacamp_db.py  # Check database
```

---

## Important Implementation Details

### Cloudflare Bypass (DataCamp)
- Uses `cloudscraper` library
- Automatically detects and solves challenges
- Transparent to the scraper interface

### Date Parsing
Multiple format attempts ensure compatibility:
```python
date_formats = [
    '%Y-%m-%d',
    '%B %d, %Y',
    '%b %d, %Y',
    '%d %B %Y',
]
```

### Author Handling
Multiple authors stored as comma-separated string:
```python
authors = ['Author 1', 'Author 2']
author_string = ', '.join(authors)  # "Author 1, Author 2"
```

### URL Normalization
All URLs converted to absolute paths:
```python
if url.startswith('/'):
    url = base_url + url
```

---

## Database Operations

### Create/Initialize
```python
SessionLocal = create_connection('scraper_data.db')
create_tables()
```

### Get or Create Author
```python
author = author_repo.get_or_create("John Doe")
# Returns existing author or creates new one
```

### Add Article with Deduplication
```python
article = article_repo.add_article_with_dedup(
    {
        'title': 'Article',
        'url': 'https://...',
        'publication_date': date(2025, 10, 18)
    },
    author
)
# Returns article if new, None if duplicate URL
```

### Query All Articles
```python
articles = article_repo.list_articles()
for article in articles:
    print(f"{article.title} by {article.author.name}")
```

---

## Error Handling

### Graceful Failures
- If webpage fetch fails → Skip that source, continue with others
- If article extraction fails → Log error, continue with next article
- If database save fails → Log error, continue with next article

### Retry Logic
Not implemented but could be added via decorator pattern.

### Logging
All errors logged with context:
```python
print(f"Failed to fetch {url}: {err}")
print(f"Error processing article: {e}")
```

---

## Performance Considerations

### Concurrent Processing
- 5 concurrent workers (configurable)
- Each worker handles one URL
- Total time ≈ max(individual_times) + threading_overhead

### Database Deduplication
- URL lookup O(log n) with proper indexing
- Prevents duplicate inserts
- Single point of truth per article

### Memory Efficiency
- Stream articles one at a time
- Don't load entire HTML into memory
- Use generators where possible

---

## Troubleshooting

### Issue: No articles extracted
- Check if website URL is correct
- Verify HTML structure hasn't changed
- Review scraper logic in corresponding class
- Check extraction rules in docs/02_EXTRACTION_RULES.md

### Issue: 403 Forbidden (DataCamp)
- Ensure cloudscraper is installed: `pip install cloudscraper`
- Verify internet connection
- Check if DataCamp has changed protection mechanism

### Issue: Database locked
- Close all database connections
- Delete `scraper_data.db` to reset
- Restart application

---

## Testing

### Run All Tests
```powershell
cd tests
pytest -v
```

### Run Specific Test
```powershell
pytest tests/test_datacamp_scraper.py -v
```

### Manual Verification
```powershell
python tests/verify_datacamp_db.py
```

---

**Last Updated**: October 18, 2025  
**Status**: Complete and Production Ready
