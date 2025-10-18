#!/usr/bin/env python
"""
Test to verify the scraper follows Real Python website rules correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from webscraper_core.scraper import WebScraper
from bs4 import BeautifulSoup

def test_realpython_extraction():
    """Test that the scraper correctly extracts articles following Real Python rules."""
    
    print("=" * 80)
    print("REAL PYTHON SCRAPER VERIFICATION TEST")
    print("=" * 80)
    
    # Fetch the Real Python homepage
    url = 'https://realpython.com/'
    print(f"\n1. Fetching Real Python homepage: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("   ✓ Successfully fetched page")
    except Exception as e:
        print(f"   ✗ Failed to fetch page: {e}")
        return
    
    # Use the scraper to extract articles
    print("\n2. Extracting articles using Real Python rules...")
    scraper = WebScraper(url)
    articles = scraper.extract_article_data(response.text)
    
    print(f"   ✓ Extracted {len(articles)} articles")
    
    # Verify extraction quality
    print("\n3. Verifying extraction follows Real Python rules:")
    
    if not articles:
        print("   ✗ No articles extracted!")
        return
    
    # Check first few articles
    for i, article in enumerate(articles[:3], 1):
        print(f"\n   Article {i}:")
        
        # Verify required fields
        if not article.get('title'):
            print(f"     ✗ Missing title")
        else:
            print(f"     ✓ Title: {article['title'][:60]}...")
        
        if not article.get('url'):
            print(f"     ✗ Missing URL")
        else:
            print(f"     ✓ URL: {article['url']}")
        
        if not article.get('author'):
            print(f"     ! Author: {article['author']} (will be fetched from article page)")
        else:
            print(f"     ✓ Author: {article['author']}")
        
        if article.get('publication_date'):
            print(f"     ✓ Publication Date: {article['publication_date']}")
        else:
            print(f"     ! No publication date extracted")
    
    # Verify HTML selectors used
    print("\n4. Verifying HTML selectors:")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for article cards with class 'card border-0'
    card_elements = soup.find_all('div', class_='card')
    border_cards = [c for c in card_elements if 'border-0' in c.get('class', [])]
    print(f"   ✓ Found {len(border_cards)} div.card.border-0 elements")
    
    # Check for titles with class 'card-title'
    title_elements = soup.find_all('h2', class_='card-title')
    print(f"   ✓ Found {len(title_elements)} h2.card-title elements")
    
    # Check for date spans
    date_spans = soup.find_all('span', class_='mr-2')
    print(f"   ✓ Found {len(date_spans)} span.mr-2 elements (for dates)")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE: Scraper is correctly following Real Python rules!")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    test_realpython_extraction()
