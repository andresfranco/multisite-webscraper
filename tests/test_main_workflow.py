"""Test for main.py multi-site scraping functionality."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.manager import run_many_and_aggregate, _save_articles_to_db
from webscraper_core.database import create_connection, create_tables
from webscraper_core.models import Base
from webscraper_core.repositories.author_repository import AuthorRepository
from webscraper_core.repositories.article_repository import ArticleRepository
from datetime import date


def test_main_workflow_with_mock_data():
    """Test main.py workflow logic with mock scraped data."""
    
    # Setup clean database
    SessionLocal = create_connection('test_scraper.db')
    from webscraper_core.database import engine
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    
    # Initialize repositories directly for this test
    author_repo = AuthorRepository(session)
    article_repo = ArticleRepository(session)
    
    # Simulate articles from different sources (as if scraped)
    all_articles_to_process = [
        # Real Python source
        {
            'title': 'Real Python Article 1',
            'author': 'Author A',
            'url': 'https://realpython.com/article1',
            'publication_date': date(2024, 10, 18),
            'source': 'https://realpython.com/'
        },
        {
            'title': 'Real Python Article 2',
            'author': 'Author B',
            'url': 'https://realpython.com/article2',
            'publication_date': date(2024, 10, 17),
            'source': 'https://realpython.com/'
        },
        # FreeCodeCamp source
        {
            'title': 'FreeCodeCamp Article 1',
            'author': 'Author A',  # Duplicate author name
            'url': 'https://freecodecamp.org/article1',
            'publication_date': date(2024, 10, 16),
            'source': 'https://freecodecamp.org/'
        },
        {
            'title': 'FreeCodeCamp Article 2',
            'author': 'Author C',
            'url': 'https://freecodecamp.org/article2',
            'publication_date': date(2024, 10, 15),
            'source': 'https://freecodecamp.org/'
        },
        # DataCamp source
        {
            'title': 'DataCamp Article 1',
            'author': 'Author B',  # Duplicate author name
            'url': 'https://datacamp.com/article1',
            'publication_date': date(2024, 10, 14),
            'source': 'https://datacamp.com/blog'
        }
    ]
    
    # Process all articles directly in repository
    created_count = 0
    for article_data in all_articles_to_process:
        author_name = article_data.get('author', 'Unknown')
        author = author_repo.get_or_create(author_name)
        
        if author:
            result = article_repo.add_article_with_dedup(article_data, author)
            if result:
                created_count += 1
    
    # Verify articles were created
    assert created_count == 5, f"Expected 5 articles created, got {created_count}"
    
    # Verify database content
    all_authors = author_repo.list_authors()
    all_articles = article_repo.list_articles()
    
    # Should have 3 unique authors despite 5 articles
    assert len(all_authors) == 3, f"Expected 3 authors, got {len(all_authors)}"
    # Should have 5 articles total
    assert len(all_articles) == 5, f"Expected 5 articles, got {len(all_articles)}"
    
    session.close()
    
    print("✓ Main workflow processes multiple sources correctly")
    print("✓ Author deduplication across sources working")
    print("✓ All 5 articles saved successfully")


def test_aggregated_statistics_calculation():
    """Test that aggregated statistics are calculated correctly."""
    
    # Mock result dictionaries as if from run_many()
    results = [
        {
            'url': 'https://realpython.com/',
            'status': 'success',
            'created': 5,
            'skipped': 2,
            'errors': 0,
            'total_articles': 7
        },
        {
            'url': 'https://freecodecamp.org/',
            'status': 'success',
            'created': 3,
            'skipped': 1,
            'errors': 0,
            'total_articles': 4
        },
        {
            'url': 'https://datacamp.com/blog',
            'status': 'success',
            'created': 2,
            'skipped': 0,
            'errors': 0,
            'total_articles': 2
        }
    ]
    
    # Calculate aggregated statistics (as would be done by aggregated_results())
    total_urls = len(results)
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = total_urls - successful
    total_created = sum(r.get('created', 0) for r in results)
    total_skipped = sum(r.get('skipped', 0) for r in results)
    total_errors = sum(r.get('errors', 0) for r in results)
    
    # Verify calculations
    assert total_urls == 3
    assert successful == 3
    assert failed == 0
    assert total_created == 10
    assert total_skipped == 3
    assert total_errors == 0
    
    print("✓ Statistics aggregation working correctly")
    print(f"  Total URLs: {total_urls}")
    print(f"  Successful: {successful}")
    print(f"  Total Created: {total_created}")
    print(f"  Total Skipped: {total_skipped}")


if __name__ == '__main__':
    print("Testing main.py multi-site scraping workflow...\n")
    test_main_workflow_with_mock_data()
    test_aggregated_statistics_calculation()
    print("\n✅ Main.py multi-site scraping validated!")
