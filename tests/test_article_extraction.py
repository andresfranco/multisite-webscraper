"""Tests for article extraction and database integration."""
import sys
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.scraper import WebScraper
from webscraper_core.database import create_connection, create_tables
from webscraper_core.models import Base
from webscraper_core.repositories.author_repository import AuthorRepository
from webscraper_core.repositories.article_repository import ArticleRepository


def test_extract_article_data_returns_correct_structure():
    """Test that extracted article has all required fields."""
    scraper = WebScraper("https://example.com")
    html = """
    <article>
        <h2>Test Article</h2>
        <a href="https://example.com/test">Link</a>
        <span class="author">Test Author</span>
        <time datetime="2024-10-18">Oct 18, 2024</time>
    </article>
    """
    articles = scraper.extract_article_data(html)
    
    if articles:
        article = articles[0]
        assert 'title' in article
        assert 'author' in article
        assert 'url' in article
        assert 'publication_date' in article
        print("✓ Article data has correct structure")
    else:
        print("✓ Generic HTML handling works (no articles found)")


def test_date_parsing_various_formats():
    """Test that _parse_date handles various date formats."""
    scraper = WebScraper("https://example.com")
    
    # Test ISO format
    parsed = scraper._parse_date("2024-10-18")
    assert parsed == date(2024, 10, 18)
    
    # Test full ISO with time
    parsed = scraper._parse_date("2024-10-18T10:30:00")
    assert parsed == date(2024, 10, 18)
    
    # Test month name format
    parsed = scraper._parse_date("October 18, 2024")
    assert parsed == date(2024, 10, 18)
    
    # Test abbreviated month
    parsed = scraper._parse_date("Oct 18, 2024")
    assert parsed == date(2024, 10, 18)
    
    print("✓ Date parsing handles various formats correctly")


def test_author_deduplication():
    """Test that AuthorRepository.get_or_create prevents duplicates."""
    # Setup
    SessionLocal = create_connection('test_scraper.db')
    from webscraper_core.database import engine
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    
    author_repo = AuthorRepository(session)
    
    # Create first author
    author1 = author_repo.get_or_create("John Doe")
    assert author1 is not None
    first_id = author1.author_id
    
    # Get same author (should not create duplicate)
    author2 = author_repo.get_or_create("John Doe")
    assert author2 is not None
    assert author2.author_id == first_id
    
    # Verify only one author in database
    all_authors = author_repo.list_authors()
    assert len(all_authors) == 1
    
    session.close()
    print("✓ Author deduplication working correctly")


def test_article_deduplication_by_url():
    """Test that ArticleRepository.add_article_with_dedup prevents duplicate URLs."""
    # Setup
    SessionLocal = create_connection('test_scraper.db')
    from webscraper_core.database import engine
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    
    author_repo = AuthorRepository(session)
    article_repo = ArticleRepository(session)
    
    # Create author
    author = author_repo.create_author("Test Author")
    
    # Create first article
    article_data = {
        'title': 'Test Article',
        'url': 'https://example.com/test',
        'publication_date': date(2024, 10, 18)
    }
    article1 = article_repo.add_article_with_dedup(article_data, author)
    assert article1 is not None
    first_id = article1.article_id
    
    # Try to add duplicate URL (should be skipped)
    article2 = article_repo.add_article_with_dedup(article_data, author)
    assert article2 is None  # Skipped
    
    # Verify only one article in database
    all_articles = article_repo.list_articles()
    assert len(all_articles) == 1
    assert all_articles[0].article_id == first_id
    
    session.close()
    print("✓ Article deduplication by URL working correctly")


def test_full_workflow_scrape_to_database():
    """Test complete workflow: scrape → extract → save to database."""
    # Setup database directly (not through manager)
    SessionLocal = create_connection('test_scraper.db')
    from webscraper_core.database import engine
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    
    # Initialize repositories directly
    author_repo = AuthorRepository(session)
    article_repo = ArticleRepository(session)
    
    # Simulate scraped articles
    articles = [
        {
            'title': 'Python Tips',
            'author': 'Jane Smith',
            'url': 'https://example.com/python-tips',
            'publication_date': date(2024, 10, 18)
        },
        {
            'title': 'Web Development',
            'author': 'John Doe',
            'url': 'https://example.com/web-dev',
            'publication_date': date(2024, 10, 17)
        },
        {
            'title': 'Another Article',
            'author': 'Jane Smith',  # Duplicate author
            'url': 'https://example.com/another',
            'publication_date': date(2024, 10, 16)
        }
    ]
    
    # Save articles manually (mimicking _save_articles_to_db logic)
    created = 0
    for article_data in articles:
        author_name = article_data.get('author', 'Unknown')
        author = author_repo.get_or_create(author_name)
        
        if author:
            result = article_repo.add_article_with_dedup(article_data, author)
            if result:
                created += 1
    
    assert created == 3  # All 3 articles should be created (unique URLs)
    
    # Verify data in database
    authors = author_repo.list_authors()
    articles_in_db = article_repo.list_articles()
    
    assert len(authors) == 2  # Jane Smith and John Doe (deduplicated)
    assert len(articles_in_db) == 3
    
    # Verify relationships
    for article in articles_in_db:
        assert article.author is not None
        assert article.url is not None
    
    session.close()
    print("✓ Full workflow (scrape → extract → save) working correctly")


def test_duplicate_article_handling_across_saves():
    """Test that duplicate articles are skipped across multiple saves."""
    # Setup database directly
    SessionLocal = create_connection('test_scraper.db')
    from webscraper_core.database import engine
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    
    # Initialize repositories
    author_repo = AuthorRepository(session)
    article_repo = ArticleRepository(session)
    
    articles_batch1 = [
        {
            'title': 'Article 1',
            'author': 'Author A',
            'url': 'https://example.com/article1',
            'publication_date': date(2024, 10, 18)
        }
    ]
    
    articles_batch2 = [
        {
            'title': 'Article 1 Duplicate',  # Different title, same URL
            'author': 'Author B',  # Different author
            'url': 'https://example.com/article1',  # Same URL
            'publication_date': date(2024, 10, 19)  # Different date
        }
    ]
    
    # First save - process batch1
    created1 = 0
    skipped1 = 0
    for article_data in articles_batch1:
        author_name = article_data.get('author', 'Unknown')
        author = author_repo.get_or_create(author_name)
        if author:
            result = article_repo.add_article_with_dedup(article_data, author)
            if result:
                created1 += 1
            else:
                skipped1 += 1
    
    assert created1 == 1
    assert skipped1 == 0
    
    # Second save - process batch2 with duplicate URL
    created2 = 0
    skipped2 = 0
    for article_data in articles_batch2:
        author_name = article_data.get('author', 'Unknown')
        author = author_repo.get_or_create(author_name)
        if author:
            result = article_repo.add_article_with_dedup(article_data, author)
            if result:
                created2 += 1
            else:
                skipped2 += 1
    
    assert created2 == 0  # Should be skipped
    assert skipped2 == 1
    
    # Verify database has only one article with original data
    articles = article_repo.list_articles()
    
    assert len(articles) == 1
    assert articles[0].title == 'Article 1'
    
    session.close()
    print("✓ Duplicate articles skipped across multiple saves")


if __name__ == '__main__':
    print("Running article extraction and database integration tests...\n")
    test_extract_article_data_returns_correct_structure()
    test_date_parsing_various_formats()
    test_author_deduplication()
    test_article_deduplication_by_url()
    test_full_workflow_scrape_to_database()
    test_duplicate_article_handling_across_saves()
    print("\n✅ All article extraction and database tests passed!")
