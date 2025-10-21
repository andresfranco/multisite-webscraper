# Grid Search Architecture & Data Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    grid.html (Template)                  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Search Input Box (with icon)                       │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ Filter Section:                                    │  │   │
│  │  │  • Author Dropdown        • Per Page Selector     │  │   │
│  │  │  • Date Dropdown          • Clear Filters Button  │  │   │
│  │  │  • Website Dropdown                                │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ Results Info (e.g., "Showing 1-10 of 47")         │  │   │
│  │  │ Filter Status (Active filters display)             │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │            Article Grid (Cards)                    │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ Pagination Controls:                               │  │   │
│  │  │  [Previous] [1] [2] [3] [Next]                     │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            grid.js (JavaScript Logic)                    │   │
│  │  • Event Listeners (Search, Filters, Pagination)        │   │
│  │  • API Communication                                     │   │
│  │  • State Management (Filters, Current Page, etc.)        │   │
│  │  • DOM Rendering                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            grid.css (Styling)                            │   │
│  │  • Filter dropdowns styling                              │   │
│  │  • Pagination buttons styling                            │   │
│  │  • Responsive design                                     │   │
│  │  • Color scheme (Orange accent)                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    (HTTP GET Requests)
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Flask Server)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           API Routes (app/routes/api.py)                │   │
│  │                                                           │   │
│  │  GET /api/articles                                        │   │
│  │    Query Parameters: search, author, date, website,       │   │
│  │                      page, per_page                       │   │
│  │    ↓                                                       │   │
│  │    Calls: ScraperService.get_filtered_articles()         │   │
│  │    ↓                                                       │   │
│  │    Returns: Paginated articles + metadata                │   │
│  │                                                           │   │
│  │  GET /api/article-filters                                 │   │
│  │    ↓                                                       │   │
│  │    Calls: ScraperService.get_filter_options()            │   │
│  │    ↓                                                       │   │
│  │    Returns: Authors, Dates, Websites lists               │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    Services (app/services/scraper_service.py)            │   │
│  │                                                           │   │
│  │  get_filtered_articles(search, author, date, website)    │   │
│  │    1. Fetch all articles from repository                 │   │
│  │    2. Format articles                                    │   │
│  │    3. Apply search filter (title/author)                 │   │
│  │    4. Apply author filter                                │   │
│  │    5. Apply date filter                                  │   │
│  │    6. Apply website filter                               │   │
│  │    7. Return filtered list                               │   │
│  │                                                           │   │
│  │  get_filter_options()                                     │   │
│  │    1. Fetch all articles                                 │   │
│  │    2. Extract unique authors                             │   │
│  │    3. Extract unique dates (sorted)                      │   │
│  │    4. Extract unique websites (sorted)                   │   │
│  │    5. Return organized filter options                    │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    Repositories (webscraper_core/repositories/)          │   │
│  │                                                           │   │
│  │  ArticleRepository                                        │   │
│  │    • list_articles() - Get all articles from DB          │   │
│  │    • delete_article()                                    │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Database (SQLite)                             │   │
│  │                                                           │   │
│  │  Tables:                                                  │   │
│  │  • articles (id, title, url, publication_date, etc.)    │   │
│  │  • authors (id, name)                                    │   │
│  │  • Article → Author (foreign key relationship)           │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### User Interaction Flow

```
┌─────────────────┐
│  User Action    │
└────────┬────────┘
         │
         ├─ Type in Search Box
         │  └─→ searchInput.addEventListener('input')
         │      └─→ updateFilters()
         │          └─→ currentPage = 1
         │              └─→ loadArticles()
         │
         ├─ Select from Dropdown
         │  └─→ filterSelect.addEventListener('change')
         │      └─→ updateFilters()
         │          └─→ currentPage = 1
         │              └─→ loadArticles()
         │
         ├─ Click Clear Filters
         │  └─→ clearFiltersBtn.addEventListener('click')
         │      └─→ resetAllFilters()
         │          └─→ loadArticles()
         │
         └─ Click Page Number
            └─→ pageButton.addEventListener('click')
                └─→ currentPage = n
                    └─→ loadArticles()
```

### API Request/Response Flow

```
Frontend (grid.js)
│
├─ On Page Load
│  │
│  ├─ Fetch: GET /api/article-filters
│  │  ├─ Response: { authors[], dates[], websites[] }
│  │  └─ Action: Populate dropdown menus
│  │
│  └─ Fetch: GET /api/articles?page=1&per_page=10
│     ├─ Response: { articles[], total_count, total_pages, ... }
│     ├─ Action: Render articles
│     └─ Action: Setup pagination controls
│
├─ On Search/Filter Change
│  │
│  └─ Fetch: GET /api/articles
│     ?search=term
│     &author=name
│     &date=2024-01-15
│     &website=https://example.com
│     &page=1
│     &per_page=10
│     │
│     └─ Backend Processing:
│        ├─ Call: get_filtered_articles(...)
│        ├─ Step 1: list_articles() [DB Query]
│        ├─ Step 2: Format articles
│        ├─ Step 3: Apply all filters (AND logic)
│        ├─ Step 4: Slice for pagination [start:end]
│        └─ Step 5: Return response
│        
│     └─ Response: { 
│        articles[]: Filtered & paginated results,
│        count: 10 (items on this page),
│        total_count: 47 (total matching filters),
│        page: 1,
│        per_page: 10,
│        total_pages: 5,
│        has_next: true,
│        has_prev: false
│     }
│
└─ On Pagination
   │
   └─ Fetch: GET /api/articles
      ?page=2
      &per_page=10
      &[existing filters...]
      │
      └─ Response: Articles 11-20 with updated metadata
```

## Component Interaction Diagram

```
┌─────────────────────────────────────┐
│     User Interface Elements         │
├─────────────────────────────────────┤
│                                     │
│  Search Input ────┐                 │
│                   │                 │
│  Author Dropdown  ├─→ grid.js ─→   │
│                   │      ↑          │
│  Date Dropdown    │      │          │
│                   │   Event         │
│  Website Dropdown ├─→ Listeners     │
│                   │      ↓          │
│  Per Page Selector│   Filter        │
│                   │   State         │
│  Clear Button ────┘                 │
│                                     │
│  Pagination Controls ──┐            │
│  (Prev, Pages, Next)   └→ Triggers  │
│                           Page      │
│                          Change     │
│                                     │
└─────────────────────────────────────┘
         ↓                  ↑
    Fetch from API    Response Update
         ↓                  ↑
┌─────────────────────────────────────┐
│        Backend API Layer            │
├─────────────────────────────────────┤
│  /api/articles                      │
│  • Parse query parameters           │
│  • Validate pagination params       │
│  • Call service layer               │
│  • Format response                  │
│  • Return JSON                      │
│                                     │
│  /api/article-filters               │
│  • Call service layer               │
│  • Extract unique values            │
│  • Return JSON                      │
└─────────────────────────────────────┘
         ↓                  ↑
    Execute Query    Retrieve Data
         ↓                  ↑
┌─────────────────────────────────────┐
│      Business Logic Layer           │
├─────────────────────────────────────┤
│  ScraperService                     │
│  • Filter articles                  │
│  • Sort options                     │
│  • Format for JSON                  │
└─────────────────────────────────────┘
         ↓                  ↑
    Query DB         Raw Data
         ↓                  ↑
┌─────────────────────────────────────┐
│      Data Access Layer              │
├─────────────────────────────────────┤
│  ArticleRepository                  │
│  • list_articles()                  │
│  • delete_article()                 │
└─────────────────────────────────────┘
         ↓                  ↑
    Execute SQL        Results
         ↓                  ↑
┌─────────────────────────────────────┐
│         SQLite Database             │
├─────────────────────────────────────┤
│  • articles table                   │
│  • authors table                    │
│  • relationships                    │
└─────────────────────────────────────┘
```

## State Management

### JavaScript State Object

```javascript
// Current Filter State
currentFilters = {
  search: "",        // Search query (title/author)
  author: "",        // Selected author
  date: "",          // Selected date
  website: ""        // Selected website
}

// Pagination State
currentPage = 1           // Current page number
currentPerPage = 10       // Items per page (5, 10, or 20)
allArticles = []         // Articles on current page

// UI State (derived from API response)
{
  count: 10,            // Articles on current page
  total_count: 47,      // Total articles matching filters
  total_pages: 5,       // Total pages available
  has_next: true,       // Can go to next page?
  has_prev: false       // Can go to previous page?
}
```

## Filtering Logic Flow

```
Input: Raw Articles from Database
│
├─ Search Filter (if search_query)
│  ├─ Title contains search_query (case-insensitive)?
│  └─ OR Author contains search_query (case-insensitive)?
│
├─ Author Filter (if author selected)
│  └─ Article author matches selected author?
│
├─ Date Filter (if date selected)
│  └─ Article date matches selected date?
│
├─ Website Filter (if website selected)
│  └─ Article website matches selected website?
│
└─ ALL filters combined with AND logic
   (Article must match ALL applied filters)
   
Output: Filtered Articles List
│
├─ Calculate Total Count
│
├─ Apply Pagination
│  ├─ Calculate total_pages = ceil(total_count / per_page)
│  ├─ Calculate start_idx = (page - 1) * per_page
│  ├─ Calculate end_idx = start_idx + per_page
│  └─ Return articles[start_idx:end_idx]
│
└─ Output: 
   {
     articles: [...],
     count: 10,
     total_count: 47,
     page: 1,
     per_page: 10,
     total_pages: 5,
     has_next: true,
     has_prev: false
   }
```

## File Dependencies

```
grid.html (Template)
  ├─ Imports: grid.css
  ├─ Imports: grid.js
  └─ Displays: Dynamic content from API

grid.css (Styling)
  ├─ Variables: Color, spacing, fonts
  ├─ Components: Filters, pagination
  └─ Responsive: Mobile, tablet, desktop

grid.js (Logic)
  ├─ Calls: /api/articles (GET)
  ├─ Calls: /api/article-filters (GET)
  ├─ Calls: /api/clear-articles (POST)
  ├─ Manages: Filter state
  ├─ Manages: Pagination state
  └─ Updates: DOM elements

api.py (Routes)
  ├─ Route: GET /api/articles
  ├─ Route: GET /api/article-filters
  ├─ Route: POST /api/clear-articles
  └─ Calls: ScraperService methods

scraper_service.py (Business Logic)
  ├─ Method: get_filtered_articles()
  ├─ Method: get_filter_options()
  ├─ Method: get_all_articles()
  └─ Calls: ArticleRepository methods

database_service.py & article_repository.py (Data Access)
  ├─ Method: list_articles()
  └─ Calls: SQLite database
```

## Performance Considerations

```
Database Query Optimization:
├─ Server-side filtering reduces data transfer
├─ Pagination limits records returned
├─ All filters applied at once (1 query vs. multiple)
└─ Results cached per page request

Frontend Optimization:
├─ Filter options loaded once on page load
├─ Page numbers generated on-demand
├─ DOM updated only when necessary
├─ Event listeners attached to parent elements (when possible)
└─ Images/content lazy loaded by browser

Scalability:
├─ Supports thousands of articles
├─ Pagination handles large datasets
├─ Responsive dropdowns don't lag with many options
└─ Database indexes recommended on title, author, date
```

## Security Considerations

```
Input Validation:
├─ Search query: Sanitized before database query
├─ Filter selections: Validated against known options
├─ Pagination: Page number must be positive integer
├─ Per page: Must be 5, 10, or 20
└─ All user input escaped for display

Data Protection:
├─ No sensitive data exposed in API responses
├─ Database queries parameterized (no SQL injection)
├─ CORS headers configured (if applicable)
└─ Authentication layer (if configured)
```

## Future Architecture Enhancements

```
Potential Improvements:
├─ Add caching layer (Redis) for filter options
├─ Implement full-text search with Elasticsearch
├─ Add database indexing on commonly filtered fields
├─ Implement request debouncing for search
├─ Add GraphQL API layer for flexibility
├─ Implement real-time updates with WebSockets
├─ Add user preferences (saved filters)
└─ Implement advanced analytics dashboard
```
