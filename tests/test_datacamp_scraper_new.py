"""Test DataCampScraper implementation."""
import sys
import os

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webscraper_core.scrapers.datacamp_scraper import DataCampScraper


def test_datacamp_scraper():
    """Test that DataCampScraper can extract article data."""
    scraper = DataCampScraper('https://www.datacamp.com/blog')

    # Fetch real homepage
    html = scraper.fetch_page()
    if not html:
        pytest.skip("Could not fetch DataCamp Blog homepage (network unavailable)")

    # Extract articles
    articles = scraper.extract_article_data(html)

    assert articles, "No articles extracted from DataCamp"

    # Verify article structure for first 3 articles
    for article in articles[:3]:
        assert article.get('title'), "Article missing title"
        assert article.get('url'), "Article missing URL"
        assert article['url'].startswith('https'), "Article URL is not absolute"


if __name__ == '__main__':
    success = test_datacamp_scraper()
    sys.exit(0 if success else 1)
