"""Specialized scraper for DataCamp Blog (https://www.datacamp.com/blog).

Follows the extraction rules in docs/DATA_CAMP_RULES.md:
1. Article cards use data-trackid attribute with format "media-card-*"
2. Article links use data-trackid with format "media-card-*"
3. Article titles are in h2 inside the anchor tag
4. Author names are in <p> tags inside elements with data-trackid="media-visit-author-profile"
5. Publication date is in a <p> tag near the bottom of the card
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
from webscraper_core.scraper import WebScraper
import time
import urllib3
import cloudscraper

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DataCampScraper(WebScraper):
    """Specialized scraper for extracting articles from DataCamp Blog."""
    
    BASE_URL = 'https://www.datacamp.com'
    
    def fetch_page(self):
        """Fetch HTML content from the URL with proper headers using cloudscraper to bypass Cloudflare."""
        try:
            # Use cloudscraper to bypass Cloudflare protection
            scraper = cloudscraper.create_scraper()
            
            # Define headers that mimic a modern browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
            }
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            
            response = scraper.get(self.url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as err:
            print(f"Failed to fetch {self.url}: {err}")
            return None
    
    def extract_article_data(self, html_content: str) -> List[dict]:
        """Extract article data from DataCamp Blog homepage.
        
        Returns a list of dictionaries with:
        - title: Article title
        - author: Author name(s)
        - url: Article URL (absolute)
        - publication_date: Publication date
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Find all article cards (div with data-trackid containing "media-card-")
        for card_elem in soup.find_all('div', attrs={'data-trackid': lambda x: x and 'media-card-' in str(x)}):
            try:
                # Extract title and URL from anchor tag with data-trackid containing "media-card-"
                title_link = card_elem.find('a', attrs={'data-trackid': lambda x: x and 'media-card-' in str(x)})
                if not title_link:
                    continue
                
                url = title_link.get('href', '').strip()
                if not url:
                    continue
                
                # Make URL absolute if relative
                if url.startswith('/'):
                    url = self.BASE_URL + url
                
                # Extract title from h2 inside the link
                title_elem = title_link.find('h2')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title:
                    continue
                
                # Extract author(s) from author profile links with data-trackid="media-visit-author-profile"
                authors = self._extract_authors(card_elem)
                author = ', '.join(authors) if authors else 'Unknown'
                
                # Extract publication date from p tag (typically the last p tag in the card)
                pub_date = self._extract_publication_date(card_elem)
                
                articles.append({
                    'title': title,
                    'author': author,
                    'url': url,
                    'publication_date': pub_date
                })
                
            except Exception as e:
                print(f"Error extracting DataCamp article: {e}")
                continue
        
        return articles
    
    def _extract_authors(self, card_elem) -> List[str]:
        """Extract author name(s) from article card.
        
        Authors are in <p> tags that are siblings to elements
        containing data-trackid="media-visit-author-profile".
        """
        authors = []
        try:
            # Find all author profile links
            for author_link in card_elem.find_all('a', attrs={'data-trackid': 'media-visit-author-profile'}):
                # Find the next p tag (sibling) that contains the author name
                parent = author_link.parent
                while parent:
                    next_p = parent.find_next('p')
                    if next_p:
                        author_name = next_p.get_text(strip=True)
                        if author_name and author_name not in authors:
                            authors.append(author_name)
                        break
                    parent = parent.parent if parent.parent else None
        except Exception as e:
            print(f"Error extracting authors: {e}")
        
        return authors
    
    def _extract_publication_date(self, card_elem) -> Optional[object]:
        """Extract publication date from article card.
        
        Date is typically in a <p> tag near the bottom of the card
        and contains text like "November 22, 2024".
        """
        try:
            # Find all p tags in the card
            p_tags = card_elem.find_all('p')
            if not p_tags:
                return None
            
            # Look through p tags for date patterns
            for p_tag in p_tags:
                date_text = p_tag.get_text(strip=True)
                # Check if p contains a date (has month and year)
                if any(month in date_text for month in ['January', 'February', 'March', 'April', 'May', 'June',
                                                          'July', 'August', 'September', 'October', 'November', 'December']):
                    return self._parse_date(date_text)
                
                # Also check for abbreviated months
                if any(month in date_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    return self._parse_date(date_text)
        except Exception as e:
            print(f"Error extracting publication date: {e}")
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[object]:
        """Parse date string into Python date object.
        
        Handles various date formats commonly found in DataCamp articles.
        """
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S%z',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]
        
        # Remove timezone info if present
        clean_date_str = date_str
        if '+' in clean_date_str:
            clean_date_str = clean_date_str.split('+')[0]
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
