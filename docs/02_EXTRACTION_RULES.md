# Data Extraction Rules by Source

This document consolidates the HTML structure rules for extracting articles from each target website.

---

## Real Python (realpython.com)

### Article Card Structure
- **Container**: `div` with class `card border-0`
- **Title**: Inside `h2` with class `card-title`
- **URL**: Inside `a` tag with `href` attribute
- **Date**: In `span` with date text (format: "Oct 15, 2025")
- **Author**: Found on individual article detail page

### Extraction Rules
1. Find all `div.card.border-0` elements
2. Extract `h2.card-title` for article title
3. Get `a href` for article URL
4. Parse date from span tags
5. Make URL absolute if relative (prepend `https://realpython.com`)

### Example HTML Pattern
```html
<div class="card border-0">
  <a href="/article-slug/">
    <h2 class="card-title">Article Title Here</h2>
  </a>
  <span class="mr-2">Oct 15, 2025</span>
</div>
```

---

## FreeCodeCamp (freecodecamp.org/news)

### Article Card Structure
- **Container**: `article` or `div.post-card`
- **Title**: Inside `h2` or `h3` tag
- **URL**: First `a` tag with `href` attribute
- **Author**: In `span.author` or `span.post-author`
- **Date**: In `time` tag with `datetime` attribute

### Extraction Rules
1. Find all `article` or `div.post-card` elements
2. Extract first heading (`h2` or `h3`) for title
3. Get first `a href` for URL
4. Find `span.author` for author name
5. Parse `time datetime` or `time` text for date

### Example HTML Pattern
```html
<article class="post-card">
  <h2><a href="/article/">Article Title</a></h2>
  <span class="author">Author Name</span>
  <time datetime="2025-10-15">October 15, 2025</time>
</article>
```

---

## DataCamp (datacamp.com/blog)

### Article Card Structure
- **Container**: `div` with `data-trackid` containing "media-card-"
- **Title**: Inside `h2` tag within article link
- **URL**: `a` tag with `data-trackid` containing "media-card-"
- **Author**: In `p` tags associated with `data-trackid="media-visit-author-profile"`
- **Date**: In `p` tag near bottom of card (contains month names)

### Extraction Rules
1. Find all `div[data-trackid*="media-card-"]` elements
2. Extract `h2` inside article link for title
3. Get `href` from link with `data-trackid` containing "media-card-"
4. Find author in `p` tags next to `data-trackid="media-visit-author-profile"`
5. Parse `p` tag with month name for publication date
6. Handle multiple authors (comma-separated)
7. Make URL absolute if relative (prepend `https://www.datacamp.com`)

### Date Parsing
Recognized month formats:
- Full months: January, February, ..., December
- Abbreviated: Jan, Feb, ..., Dec

### Example HTML Pattern
```html
<div data-trackid="media-card-How to Learn Python">
  <a data-trackid="media-card-/blog/article-slug" href="/blog/article-slug">
    <h2>How to Learn Python</h2>
  </a>
  <a data-trackid="media-visit-author-profile" href="/portfolio/author">
    <img src="...">
  </a>
  <p>Author Name</p>
  <p>November 22, 2024</p>
</div>
```

### Special Notes
- ⚠️ DataCamp uses Cloudflare protection - requires `cloudscraper` library
- ⚠️ Class names are dynamic - rely on HTML structure and `data-trackid` attributes
- ⚠️ Some articles may not have author info readily available

---

## Supported Date Formats

| Format | Example |
|--------|---------|
| %Y-%m-%d | 2025-10-18 |
| %B %d, %Y | October 18, 2025 |
| %b %d, %Y | Oct 18, 2025 |
| %d %B %Y | 18 October 2025 |
| ISO 8601 | 2025-10-18T15:30:00+00:00 |

---

## Extraction Common Patterns

### URL Normalization
- If URL starts with `/` → prepend base URL
- If URL starts with `http://` or `https://` → use as-is
- Remove query parameters and fragments if needed

### Author Handling
- Single author: Store as string
- Multiple authors: Store comma-separated or as list
- Unknown author: Store as "Unknown"
- Multiple `<p>` tags: Join all author names

### Date Handling
- If date missing: Store as `None`
- Parse using multiple format attempts
- Clean timezone info before parsing
- Convert to Python `date` object

---

## Rules Maintenance

### When HTML Structure Changes
1. Test extraction with current website
2. Inspect HTML to find new selectors
3. Update corresponding scraper class
4. Run tests to verify extraction
5. Update this document

### How to Test
```powershell
# Run scraper for specific source
python test_datacamp_extraction.py       # for DataCamp
python tests/verify_datacamp_db.py       # verify results
```

---

**Last Updated**: October 18, 2025  
**Status**: All rules validated and working
