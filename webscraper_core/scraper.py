"""
Upgraded WebScraper to extract full article data instead of just titles.
Extracts: title, author, URL, and publication_date from each article.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import time


class WebScraper:
    """Responsible for fetching a URL and extracting rich article data."""

    def __init__(self, url: str):
        self.url = url

    def fetch_page(self):
        """Fetch HTML content from the URL."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as err:
            print(f"Failed to fetch {self.url}: {err}")
            return None

    def extract_article_data(self, html_content: str) -> List[dict]:
        """Extract article data (title, author, url, publication_date) from HTML.
        
        Returns a list of dictionaries with article information.
        Handles different HTML structures for different websites.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Try to detect which website we're scraping and use appropriate selectors
        if 'realpython.com' in self.url:
            articles = self._extract_realpython_articles(soup)
        elif 'freecodecamp.org' in self.url:
            articles = self._extract_freecodecamp_articles(soup)
        elif 'datacamp.com' in self.url:
            articles = self._extract_datacamp_articles(soup)
        else:
            # Fallback to generic extraction
            articles = self._extract_generic_articles(soup)
        
        return articles

    def _extract_realpython_articles(self, soup: BeautifulSoup) -> List[dict]:
        """Extract articles from Real Python (https://realpython.com).
        
        According to Real Python rules:
        1. Article cards are in div class "card border-0"
        2. URL is in anchor tag <a> inside the card
        3. Title is in h2 tag with class "card-title h4 my-0 py-0"
        4. Author info is on individual article pages
        5. Publication date is in span with date text
        """
        articles = []
        
        # Real Python article cards have class 'card border-0'
        for card_elem in soup.find_all('div', class_='card'):
            try:
                # Skip cards that don't have the border-0 class (the border-0 filter)
                if 'border-0' not in card_elem.get('class', []):
                    continue
                
                # Extract URL from anchor tag <a href="...">
                link_elem = card_elem.find('a', href=True)
                if not link_elem:
                    continue
                    
                url = link_elem.get('href', '')
                if not url:
                    continue
                
                # Make URL absolute if relative
                if url.startswith('/'):
                    url = 'https://realpython.com' + url
                
                # Extract title from h2 with class "card-title"
                title_elem = card_elem.find('h2', class_='card-title')
                if not title_elem:
                    # Fallback to any h2 in the card
                    title_elem = card_elem.find('h2')
                
                title = title_elem.get_text(strip=True) if title_elem else None
                if not title:
                    continue
                
                # Extract publication date from span (usually says "Oct 15, 2025" format)
                # Look for span with date text
                pub_date = None
                card_text = card_elem.get_text()
                # Try to find date patterns like "Oct 15, 2025"
                for span in card_elem.find_all('span', class_='mr-2'):
                    date_text = span.get_text(strip=True)
                    if any(month in date_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                        pub_date = self._parse_date(date_text)
                        break
                
                # Author info is on the individual article page, not the homepage
                # We'll fetch it when we process the article detail page
                # For now, set it to Unknown and retrieve it from article detail page
                author = 'Unknown'
                
                articles.append({
                    'title': title,
                    'author': author,
                    'url': url,
                    'publication_date': pub_date
                })
                
            except Exception as e:
                print(f"Error extracting Real Python article: {e}")
                continue
        
        return articles

    def _extract_freecodecamp_articles(self, soup: BeautifulSoup) -> List[dict]:
        """Extract articles from freeCodeCamp News (https://www.freecodecamp.org/news)."""
        articles = []
        
        # freeCodeCamp uses article cards with class 'post-card'
        for article_elem in soup.find_all('article', class_=['post-card', 'article']):
            try:
                # Extract title
                title_elem = article_elem.find('h2') or article_elem.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                
                # Extract URL
                link_elem = article_elem.find('a', href=True)
                url = link_elem.get('href', '') if link_elem else ''
                
                # Extract author
                author_elem = article_elem.find('span', class_=['author', 'post-author'])
                author = author_elem.get_text(strip=True) if author_elem else 'Unknown'
                
                # Extract publication date
                time_elem = article_elem.find('time')
                pub_date = None
                if time_elem:
                    date_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
                    pub_date = self._parse_date(date_str)
                
                if title and url:
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

    def _extract_datacamp_articles(self, soup: BeautifulSoup) -> List[dict]:
        """Extract articles from DataCamp Blog (https://www.datacamp.com/blog)."""
        articles = []
        
        # DataCamp uses article cards with various classes
        for article_elem in soup.find_all(['article', 'div'], class_=['card', 'post', 'blog-card']):
            try:
                # Extract title
                title_elem = article_elem.find(['h2', 'h3', 'a'])
                title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                
                # Extract URL
                link_elem = article_elem.find('a', href=True)
                url = link_elem.get('href', '') if link_elem else ''
                
                # Make URL absolute if relative
                if url and url.startswith('/'):
                    url = 'https://www.datacamp.com' + url
                
                # Extract author
                author_elem = article_elem.find(['span', 'p'], class_=['author', 'by-line'])
                author = author_elem.get_text(strip=True) if author_elem else 'Unknown'
                
                # Extract publication date
                time_elem = article_elem.find('time')
                pub_date = None
                if time_elem:
                    date_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
                    pub_date = self._parse_date(date_str)
                
                if title and url:
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

    def _extract_generic_articles(self, soup: BeautifulSoup) -> List[dict]:
        """Generic article extraction for unknown websites.
        
        Attempts to find articles using common HTML patterns.
        """
        articles = []
        
        # Look for article elements
        for article_elem in soup.find_all(['article', 'div'], class_=['article', 'post', 'card']):
            try:
                # Extract title from heading
                title_elem = article_elem.find(['h2', 'h3', 'h1'])
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title:
                    continue
                
                # Extract URL
                link_elem = article_elem.find('a', href=True)
                url = link_elem.get('href', '') if link_elem else ''
                
                if not url:
                    continue
                
                # Extract author
                author_elem = article_elem.find(['span', 'p'], class_=['author', 'by'])
                author = author_elem.get_text(strip=True) if author_elem else 'Unknown'
                
                # Extract date
                time_elem = article_elem.find('time')
                pub_date = None
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
                print(f"Error extracting generic article: {e}")
                continue
        
        return articles

    def fetch_realpython_author(self, article_url: str) -> Optional[str]:
        """Fetch author name from individual Real Python article page.
        
        According to Real Python rules:
        - Author name is in div class="card mt-3" with id="author"
        - Specifically in a strong tag inside a p tag with class="card-header h3"
        
        Includes rate limiting to avoid 429 errors.
        """
        try:
            # Add delay to avoid rate limiting (2 seconds between requests)
            time.sleep(2)
            
            response = requests.get(article_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find author card: div class="card mt-3" with id="author"
            author_card = soup.find('div', class_='card', id='author')
            if not author_card:
                return None
            
            # Find p tag with class "card-header"
            header_p = author_card.find('p', class_='card-header')
            if not header_p:
                return None
            
            # Find strong tag inside the p tag
            strong_tag = header_p.find('strong')
            if not strong_tag:
                return None
            
            author_name = strong_tag.get_text(strip=True)
            return author_name if author_name else None
            
        except requests.exceptions.Timeout:
            print(f"Timeout fetching author from {article_url}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limited (429) - backing off from {article_url}")
            else:
                print(f"HTTP error fetching author from {article_url}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching author from {article_url}: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[object]:
        """Parse date string into Python date object.
        
        Handles various date formats commonly found in web articles.
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
        if '+' in date_str:
            date_str = date_str.split('+')[0]
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.date()
            except ValueError:
                continue
        
        # If no format matched, return None
        print(f"Warning: Could not parse date '{date_str}'")
        return None

    def scrape(self, response_text: str | None = None) -> List[dict]:
        """Scrape and return article data.
        
        If response_text is provided, uses that instead of fetching.
        Returns list of article dictionaries.
        """
        if response_text is None:
            response_text = self.fetch_page()
            if response_text is None:
                return []
        
        return self.extract_article_data(response_text)

    def extract_titles(self, html_content: str) -> List[str]:
        """Legacy method: Extract only titles from HTML (for backward compatibility)."""
        soup = BeautifulSoup(html_content, 'html.parser')
        titles = [h2.get_text() for h2 in soup.find_all('h2')]
        if not titles:
            titles = [tag.get_text() for tag in soup.find_all(class_='card-title')]
        return titles
