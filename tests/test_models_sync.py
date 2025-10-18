"""Quick test to verify models and repositories sync correctly."""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.database import create_connection, create_tables, Author, Article
from webscraper_core.models import Base
from webscraper_core.repositories.author_repository import AuthorRepository
from webscraper_core.repositories.article_repository import ArticleRepository
from sqlalchemy import create_engine

# Initialize DB
print("Initializing database...")
SessionLocal = create_connection('test_scraper.db')

# Get the engine for this database
from webscraper_core.database import engine

# Drop all existing tables and recreate them
print("Dropping and recreating tables...")
Base.metadata.drop_all(bind=engine)
create_tables()

# Create a session
session = SessionLocal()

# Test AuthorRepository
print("\nTesting AuthorRepository...")
author_repo = AuthorRepository(session)

# Test get_or_create - should create new author
author1 = author_repo.get_or_create("John Doe")
print(f"Created/Got author: {author1}")

# Test get_or_create - should return existing (no duplicate)
author1_again = author_repo.get_or_create("John Doe")
print(f"Got existing author (should be same): {author1_again}")
print(f"Same author ID: {author1.author_id == author1_again.author_id}")

# Test ArticleRepository
print("\nTesting ArticleRepository...")
article_repo = ArticleRepository(session)

# Test add_article_with_dedup - should create article
article_data = {
    'title': 'Python Tips & Tricks',
    'url': 'https://example.com/python-tips',
    'publication_date': datetime.strptime('2024-10-18', '%Y-%m-%d').date()
}
article1 = article_repo.add_article_with_dedup(article_data, author1)
print(f"Created article: {article1}")

# Test add_article_with_dedup - should skip duplicate URL
article_dup = article_repo.add_article_with_dedup(article_data, author1)
print(f"Attempted duplicate (should be None): {article_dup}")

# Create another article with different URL
article_data2 = {
    'title': 'Web Scraping Guide',
    'url': 'https://example.com/web-scraping',
    'publication_date': datetime.strptime('2024-10-17', '%Y-%m-%d').date()
}
article2 = article_repo.add_article_with_dedup(article_data2, author1)
print(f"Created second article: {article2}")

# List all
print("\nAll authors:")
for author in author_repo.list_authors():
    print(f"  {author}")

print("\nAll articles:")
for article in article_repo.list_articles():
    print(f"  {article}")

session.close()
print("\nTest completed successfully!")
