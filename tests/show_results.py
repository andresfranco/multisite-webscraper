#!/usr/bin/env python
"""
Complete demonstration script showing the web scraper working end-to-end
with Real Python article extraction and database storage.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import sys
from webscraper_core.database import create_connection
from webscraper_core.models import Article, Author

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*80}")
    print(f"  {text:<76}  ")
    print(f"{'='*80}\n")

def main():
    print_header("REAL PYTHON WEB SCRAPER - FINAL DEMONSTRATION")
    
    # Connect to database
    print("1. Connecting to database...")
    db_path = Path(__file__).parent.parent / 'scraper_data.db'
    SessionLocal = create_connection(str(db_path))
    if SessionLocal is None:
        print("   ❌ Failed to connect")
        return False
    
    session = SessionLocal()
    print("   ✓ Successfully connected to scraper_data.db")
    
    # Get statistics
    article_count = session.query(Article).count()
    author_count = session.query(Author).count()
    
    print(f"\n2. Database Statistics:")
    print(f"   • Total Articles: {article_count}")
    print(f"   • Total Authors: {author_count}")
    
    # Show all articles
    print(f"\n3. All Scraped Real Python Articles:\n")
    print(f"{'ID':<4} {'Title':<50} {'Date':<12} {'Author':<15}")
    print("-" * 80)
    
    articles = session.query(Article).order_by(Article.article_id).all()
    for article in articles:
        author = session.query(Author).filter(Author.author_id == article.author_id).first()
        author_name = author.name if author else "Unknown"
        title = article.title[:47] + "..." if len(article.title) > 50 else article.title
        print(f"{article.article_id:<4} {title:<50} {str(article.publication_date):<12} {author_name:<15}")
    
    # Show URLs
    print(f"\n4. All Article URLs:\n")
    for i, article in enumerate(articles, 1):
        print(f"   {i:2d}. {article.url}")
    
    # Summary statistics by author
    print(f"\n5. Articles by Author:\n")
    authors = session.query(Author).all()
    for author in authors:
        count = session.query(Article).filter(Article.author_id == author.author_id).count()
        print(f"   • {author.name:<30} - {count} article(s)")
    
    # Show data validation
    print(f"\n6. Data Validation Results:\n")
    validation_checks = []
    
    # Check all articles have titles
    articles_with_title = session.query(Article).filter(Article.title != '').count()
    validation_checks.append(("All articles have titles", articles_with_title == article_count))
    
    # Check all articles have URLs
    articles_with_url = session.query(Article).filter(Article.url != '').count()
    validation_checks.append(("All articles have URLs", articles_with_url == article_count))
    
    # Check all URLs are unique
    unique_urls = session.query(Article.url).distinct().count()
    validation_checks.append(("All URLs are unique", unique_urls == article_count))
    
    # Check all URLs are absolute
    absolute_urls = session.query(Article).filter(Article.url.like('https://%')).count()
    validation_checks.append(("All URLs are absolute", absolute_urls == article_count))
    
    # Check real python domain
    realpython_count = session.query(Article).filter(Article.url.like('%realpython.com%')).count()
    validation_checks.append(("All articles from realpython.com", realpython_count == article_count))
    
    for check_name, result in validation_checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")
    
    # Final summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(result for _, result in validation_checks)
    
    if all_passed and article_count > 0:
        print("✅ ALL CHECKS PASSED!\n")
        print(f"   Successfully extracted {article_count} articles from Real Python")
        print(f"   All articles stored in database with proper structure")
        print(f"   Data integrity validated")
        print(f"\n🚀 Web Scraper Implementation: COMPLETE AND VERIFIED")
        return True
    else:
        print("❌ Some checks failed")
        return False
    
    session.close()

if __name__ == '__main__':
    success = main()
    print(f"\n{'='*80}\n")
    sys.exit(0 if success else 1)
