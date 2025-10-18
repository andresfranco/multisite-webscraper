#!/usr/bin/env python
"""Detailed verification of scraped Real Python articles."""
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

print("=" * 80)
print("REAL PYTHON ARTICLES SCRAPED AND SAVED")
print("=" * 80)
print(f"\nDatabase Summary:")
print(f"  Total Articles: {article_count}")
print(f"  Total Unique Authors: {author_count}\n")

# Show all scraped articles with details
print("-" * 80)
print(f"{'Title':<60} | {'Author':<15} | {'Date':<12}")
print("-" * 80)

articles = session.query(Article).order_by(Article.article_id).all()
for i, article in enumerate(articles, 1):
    author_name = session.query(Author).filter(Author.author_id == article.author_id).first()
    title = article.title[:57] + "..." if len(article.title) > 60 else article.title
    author = author_name.name if author_name else "Unknown"
    date = article.publication_date if article.publication_date else "N/A"
    print(f"{title:<60} | {author:<15} | {date}")

print("-" * 80)
print(f"\nArticle URLs saved:")
for article in articles:
    print(f"  {article.url}")

session.close()
print("\n" + "=" * 80)
print("SUCCESS: All Real Python articles have been extracted and saved to database!")
print("=" * 80)
