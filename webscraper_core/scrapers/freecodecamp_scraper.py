"""Specialized scraper for freeCodeCamp (https://www.freecodecamp.org).

Follows the extraction rules in docs/FREE_CODE_CAMP_RULES.md:
1. Article titles are in h2.post-card-title with anchor tag <a>
2. Article links are in the same anchor tag
3. Author name is in <a> tag inside article card with article detail page link
4. Publication date is in <time> tag with datetime attribute
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import time
from webscraper_core.scraper import WebScraper


class FreeCodeCampScraper(WebScraper):
    """Specialized scraper for extracting articles from freeCodeCamp."""
    
    BASE_URL = 'https://www.freecodecamp.org'
    NEWS_BASE_URL = 'https://www.freecodecamp.org/news'
    RATE_LIMIT_DELAY = 1  # seconds between requests
    
    def extract_article_data(self, html_content: str) -> List[dict]:
        """Extract article data from freeCodeCamp News homepage.
        
        Returns a list of dictionaries with:
        - title: Article title
        - author: Author name
        - url: Article URL (absolute)
        - publication_date: Publication date
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # freeCodeCamp News uses div elements with class 'post-card-content'
        # These are nested inside elements with class 'post-card'
        for post_card in soup.find_all('div', class_='post-card-content'):
            try:
                # Extract title from h2.post-card-title > a
                title_elem = post_card.find('h2', class_='post-card-title')
                if not title_elem:
                    # Try to find h2 anywhere in post-card
                    parent_post = post_card.find_parent('div', class_='post-card')
                    if parent_post:
                        title_elem = parent_post.find('h2')
                
                if not title_elem:
                    continue
                
                title_link = title_elem.find('a', href=True)
                if not title_link:
                    # Try parent link if h2 doesn't have it
                    parent_div = title_elem.parent
                    while parent_div:
                        title_link = parent_div.find('a', href=True)
                        if title_link:
                            break
                        parent_div = parent_div.parent
                
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                if not title:
                    continue
                
                url = title_link.get('href', '').strip()
                if not url:
                    continue
                
                # Make URL absolute if relative
                if url.startswith('/'):
                    url = self.NEWS_BASE_URL + url
                
                # Extract author and publication date from footer
                author = 'Unknown'
                pub_date = None
                
                # Look for post-card-meta (footer with author and date info)
                footer = post_card.find('footer', class_='post-card-meta')
                if not footer:
                    # Try finding in parent post-card
                    parent_post = post_card.find_parent('div', class_='post-card')
                    if parent_post:
                        footer = parent_post.find('footer', class_='post-card-meta')
                
                if footer:
                    # Extract author from author-list
                    author_elem = footer.find('a', class_='meta-item')
                    if author_elem:
                        author = author_elem.get_text(strip=True)
                    
                    # Extract publication date from time element
                    time_elem = footer.find('time')
                    if time_elem:
                        date_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
                        pub_date = self._parse_date(date_str)
                
                articles.append({
                    'title': title,
                    'author': author,
                    'url': url,
                    'publication_date': pub_date
                })
                
            except Exception as e:
                print(f"Error extracting freeCodeCamp article: {e}")
                continue
        
        return articles
    
    def _fetch_article_details(self, article_url: str) -> dict:
        """Fetch additional details from article detail page if needed.
        
        Currently not needed as author and date are in the homepage,
        but this method can be extended for additional metadata.
        """
        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            response = requests.get(article_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract details from article page
            details = {}
            
            # Author is in section.author-card > span.author-card-name > a
            author_card = soup.find('section', class_='author-card')
            if author_card:
                author_link = author_card.find('span', class_='author-card-name')
                if author_link:
                    author_text = author_link.find('a')
                    if author_text:
                        details['author'] = author_text.get_text(strip=True)
            
            # Date is in time.post-full-meta-date
            date_elem = soup.find('time', class_='post-full-meta-date')
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                details['publication_date'] = self._parse_date(date_str)
            
            return details
            
        except Exception as e:
            print(f"Error fetching freeCodeCamp article details from {article_url}: {e}")
            return {}
    
    def _parse_date(self, date_str: str) -> Optional[object]:
        """Parse date string into Python date object.
        
        Handles various date formats commonly found in freeCodeCamp articles.
        """
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]
        
        # Remove timezone info and time if present
        clean_date_str = date_str
        if '+' in clean_date_str:
            clean_date_str = clean_date_str.split('+')[0]
        if 'Z' in clean_date_str:
            clean_date_str = clean_date_str.replace('Z', '')
        if 'T' in clean_date_str:
            clean_date_str = clean_date_str.split('T')[0]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(clean_date_str.strip(), fmt)
                return parsed_date.date()
            except ValueError:
                continue
        
        # If no format matched, return None
        return None
