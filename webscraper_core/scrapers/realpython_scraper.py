"""Specialized scraper for Real Python (https://realpython.com).

Follows the extraction rules in docs/REAL_PYTHON_RULES.md:
1. Article cards are in div class "card border-0"
2. URL is in anchor tag <a> inside the card
3. Title is in h2 tag with class "card-title"
4. Author info is on individual article pages (div id="author")
5. Publication date is in span with date text
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import time
from webscraper_core.scraper import WebScraper


class RealPythonScraper(WebScraper):
    """Specialized scraper for extracting articles from Real Python."""

    BASE_URL = "https://realpython.com"
    RATE_LIMIT_DELAY = 2  # seconds between requests to article detail pages

    def extract_article_data(self, html_content: str) -> List[dict]:
        """Extract article data from Real Python homepage.

        Returns a list of dictionaries with:
        - title: Article title
        - author: 'Unknown' (will be fetched during database save to avoid timeouts)
        - url: Article URL (absolute)
        - publication_date: Publication date
        """
        soup = BeautifulSoup(html_content, "html.parser")
        articles = []

        # Real Python article cards have class 'card border-0'
        for card_elem in soup.find_all("div", class_="card"):
            try:
                # Filter: only keep cards with 'border-0' class
                if "border-0" not in card_elem.get("class", []):
                    continue

                # Extract URL from anchor tag <a href="...">
                link_elem = card_elem.find("a", href=True)
                if not link_elem:
                    continue

                url = link_elem.get("href", "").strip()
                if not url:
                    continue

                # Make URL absolute if relative
                if url.startswith("/"):
                    url = self.BASE_URL + url

                # Extract title from h2 with class "card-title"
                title_elem = card_elem.find("h2", class_="card-title")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if not title:
                    continue

                # Extract publication date from span (usually "Oct 15, 2025" format)
                pub_date = self._extract_publication_date(card_elem)

                # Note: Author information is NOT fetched here to avoid N+1 requests
                # and potential timeouts. Authors will be fetched during database save
                # when processing articles with 'Unknown' author status.

                articles.append(
                    {
                        "title": title,
                        "author": "Unknown",
                        "url": url,
                        "publication_date": pub_date,
                    }
                )

            except Exception as e:
                print(f"Error extracting Real Python article: {e}")
                continue

        return articles

    def _extract_publication_date(self, card_elem) -> Optional[object]:
        """Extract publication date from article card.

        Date is typically in a span with class 'mr-2' containing text like "Oct 15, 2025".
        """
        try:
            # Look for span with class 'mr-2' which contains the date
            for span in card_elem.find_all("span", class_="mr-2"):
                date_text = span.get_text(strip=True)
                # Check if span contains a date (has month name)
                if any(
                    month in date_text
                    for month in [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ]
                ):
                    return self._parse_date(date_text)
        except Exception as e:
            print(f"Error extracting publication date: {e}")

        return None

    def _fetch_author_from_detail_page(self, article_url: str) -> Optional[str]:
        """Fetch author name from individual Real Python article page.

        According to Real Python rules:
        - Primary: Author name is in div class="card mt-3" with id="author"
        - Specifically in a strong tag inside a p tag with class="card-header h3"
        - Fallback: If author card not found, look for p tag with class "card-header h3"
          anywhere on the page and extract the strong tag text

        Includes rate limiting to avoid 429 errors.
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

            response = requests.get(article_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Primary method: Find author card: div class="card mt-3" with id="author"
            author_card = soup.find("div", class_="card", id="author")
            if author_card:
                # Find p tag with class "card-header"
                header_p = author_card.find("p", class_="card-header")
                if header_p:
                    # Find strong tag inside the p tag
                    strong_tag = header_p.find("strong")
                    if strong_tag:
                        author_name = strong_tag.get_text(strip=True)
                        if author_name:
                            return author_name

            # Fallback method: Look for p tag with class "card-header h3" anywhere on page
            # This handles cases where the author info is not in the div#author card
            header_p_fallback = soup.find("p", class_="card-header")
            if header_p_fallback:
                # Find strong tag inside the p tag
                strong_tag = header_p_fallback.find("strong")
                if strong_tag:
                    author_name = strong_tag.get_text(strip=True)
                    if author_name:
                        return author_name

            return None

        except requests.exceptions.Timeout:
            print(f"Timeout fetching author from {article_url}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limited (429) - skipping author fetch for {article_url}")
            else:
                print(f"HTTP error fetching author from {article_url}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching author from {article_url}: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[object]:
        """Parse date string into Python date object.

        Handles various date formats commonly found in articles.
        """
        if not date_str:
            return None

        # Common date formats to try
        date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S%z",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]

        # Remove timezone info and time if present
        if "+" in date_str:
            date_str = date_str.split("+")[0]
        if "T" in date_str:
            date_str = date_str.split("T")[0]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.date()
            except ValueError:
                continue

        # If no format matched, return None
        return None
