"""Test RealPythonScraper implementation."""
import sys
import os

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webscraper_core.scrapers.realpython_scraper import RealPythonScraper


def test_realpython_scraper():
    """Test that RealPythonScraper can extract article data."""
    scraper = RealPythonScraper('https://realpython.com/')

    # Fetch real homepage
    html = scraper.fetch_page()
    if not html:
        pytest.skip("Could not fetch Real Python homepage (network unavailable)")

    # Extract articles
    articles = scraper.extract_article_data(html)

    assert articles, "No articles extracted from Real Python"

    # Verify article structure for first 3 articles
    for article in articles[:3]:
        assert article.get('title'), "Article missing title"
        assert article.get('url'), "Article missing URL"
        assert article['url'].startswith('https'), "Article URL is not absolute"


if __name__ == '__main__':
    success = test_realpython_scraper()
    sys.exit(0 if success else 1)
