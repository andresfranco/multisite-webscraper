"""Test FreeCodeCampScraper implementation."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webscraper_core.scrapers.freecodecamp_scraper import FreeCodeCampScraper


def test_freecodecamp_scraper():
    """Test that FreeCodeCampScraper can extract article data."""
    print("[TEST] Testing FreeCodeCampScraper...")
    
    scraper = FreeCodeCampScraper('https://www.freecodecamp.org/news')
    
    # Fetch real homepage
    html = scraper.fetch_page()
    if not html:
        print("[FAIL] Failed to fetch freeCodeCamp News homepage")
        return False
    
    # Extract articles
    articles = scraper.extract_article_data(html)
    
    if not articles:
        print("[FAIL] No articles extracted")
        return False
    
    print(f"[OK] Extracted {len(articles)} articles from freeCodeCamp")
    
    # Verify article structure
    for i, article in enumerate(articles[:3], 1):
        print(f"\nArticle {i}:")
        print(f"  Title: {article.get('title', 'N/A')[:60]}...")
        print(f"  Author: {article.get('author', 'Unknown')}")
        print(f"  URL: {article.get('url', 'N/A')}")
        print(f"  Date: {article.get('publication_date', 'N/A')}")
        
        # Validate required fields
        if not article.get('title'):
            print("[FAIL] Missing title")
            return False
        if not article.get('url'):
            print("[FAIL] Missing URL")
            return False
        if not article.get('url').startswith('https'):
            print("[FAIL] URL is not absolute")
            return False
    
    print("\n[OK] FreeCodeCampScraper test passed!")
    return True


if __name__ == '__main__':
    success = test_freecodecamp_scraper()
    sys.exit(0 if success else 1)
