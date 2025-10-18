#!/usr/bin/env python3
"""
Standalone script to test DataCamp blog data extraction.

This script demonstrates how to use the DataCampScraper to extract articles
from the DataCamp blog at https://www.datacamp.com/blog
"""

import sys
import json
from datetime import datetime

# Add the project root to the path to import modules
sys.path.insert(0, __file__.rsplit('\\', 1)[0])

from webscraper_core.scrapers.datacamp_scraper import DataCampScraper


def format_article(article: dict) -> str:
    """Format an article dictionary for display."""
    return f"""
📰 Title: {article.get('title', 'N/A')}
👤 Author(s): {article.get('author', 'N/A')}
🔗 URL: {article.get('url', 'N/A')}
📅 Published: {article.get('publication_date', 'N/A')}
"""


def main():
    """Extract and display DataCamp blog articles."""
    
    print("=" * 80)
    print("DataCamp Blog Article Extraction Test")
    print("=" * 80)
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target URL: https://www.datacamp.com/blog\n")
    
    try:
        # Initialize the scraper
        scraper = DataCampScraper('https://www.datacamp.com/blog')
        print("[1] Initialized DataCampScraper")
        
        # Fetch the page
        print("[2] Fetching page content...")
        html_content = scraper.fetch_page()
        
        if not html_content:
            print("❌ Failed to fetch page content")
            return 1
        
        print(f"    ✓ Successfully fetched {len(html_content)} bytes")
        
        # Extract articles
        print("[3] Extracting article data...")
        articles = scraper.extract_article_data(html_content)
        
        if not articles:
            print("❌ No articles found")
            return 1
        
        print(f"    ✓ Found {len(articles)} articles\n")
        
        # Display results
        print("=" * 80)
        print(f"EXTRACTED ARTICLES ({len(articles)} total)")
        print("=" * 80)
        
        for i, article in enumerate(articles, 1):
            print(f"\n[Article {i}]")
            print(format_article(article))
        
        # Summary statistics
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total Articles Extracted: {len(articles)}")
        
        # Count articles with missing fields
        missing_title = sum(1 for a in articles if not a.get('title'))
        missing_author = sum(1 for a in articles if a.get('author') == 'Unknown')
        missing_date = sum(1 for a in articles if not a.get('publication_date'))
        missing_url = sum(1 for a in articles if not a.get('url'))
        
        if missing_title > 0:
            print(f"⚠️  Articles with missing title: {missing_title}")
        if missing_author > 0:
            print(f"⚠️  Articles with unknown author: {missing_author}")
        if missing_date > 0:
            print(f"⚠️  Articles with missing date: {missing_date}")
        if missing_url > 0:
            print(f"⚠️  Articles with missing URL: {missing_url}")
        
        if missing_title == 0 and missing_author == 0 and missing_date == 0 and missing_url == 0:
            print("✓ All fields successfully extracted!")
        
        # Save results to JSON file
        output_file = 'datacamp_articles.json'
        articles_data = []
        for article in articles:
            articles_data.append({
                'title': article.get('title'),
                'author': article.get('author'),
                'url': article.get('url'),
                'publication_date': str(article.get('publication_date')) if article.get('publication_date') else None
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        print(f"✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
