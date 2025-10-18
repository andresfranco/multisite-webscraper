#!/usr/bin/env python
"""Quick script to check database content."""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.database import create_connection
from webscraper_core.models import Article, Author

# Connect to database
db_path = Path(__file__).parent.parent / 'scraper_data.db'
SessionLocal = create_connection(str(db_path))
if SessionLocal is None:
    print("Failed to connect to database")
    exit(1)

session = SessionLocal()

# Count articles and authors
article_count = session.query(Article).count()
author_count = session.query(Author).count()

print(f"Total articles in DB: {article_count}")
print(f"Total authors in DB: {author_count}")

# Show recent articles
print("\nRecent articles:")
articles = session.query(Article).limit(10).all()
for article in articles:
    print(f"  - {article.title[:60]}... (Author ID: {article.author_id})")
    print(f"    URL: {article.url}")
    print(f"    Date: {article.publication_date}")

session.close()
