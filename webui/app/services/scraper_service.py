"""
Scraper Service
===============
Service module for web scraping operations.
"""

from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from webscraper_core import manager
from webscraper_core.repositories.article_repository import ArticleRepository
from webscraper_core.repositories.author_repository import AuthorRepository


class ScraperService:
    """Service for managing web scraping operations."""

    def __init__(self, db_session: Session):
        """
        Initialize ScraperService.

        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.session = db_session
        self.article_repo = ArticleRepository(db_session)
        self.author_repo = AuthorRepository(db_session)

    def scrape_urls(
        self, urls: List[str], max_workers: int = 3
    ) -> Tuple[List[Dict], Dict]:
        """
        Scrape multiple URLs and save articles to database.

        Args:
            urls: List of URLs to scrape
            max_workers: Number of worker threads to use

        Returns:
            Tuple of (results, stats) from the scraper manager

        Raises:
            ValueError: If URLs list is empty
        """
        if not urls:
            raise ValueError("At least one URL must be provided")

        try:
            results, stats = manager.run_many_and_aggregate(
                urls, max_workers=max_workers
            )
            return results, stats
        except Exception as e:
            raise RuntimeError(f"Scraping failed: {str(e)}")

    def get_all_articles(self) -> List[Dict]:
        """
        Retrieve all articles from database.

        Returns:
            List of article dictionaries with formatted data
        """
        articles = self.article_repo.list_articles()
        return self._format_articles(articles)

    def get_filtered_articles(
        self,
        search_query: str = "",
        author: str = "",
        date_from: str = "",
        date_to: str = "",
        website: str = "",
    ) -> List[Dict]:
        """
        Retrieve articles with multiple filters applied.

        Args:
            search_query: Search term for title/author (case-insensitive)
            author: Filter by author name (case-insensitive, partial match)
            date_from: Start date for range filter (YYYY-MM-DD format)
            date_to: End date for range filter (YYYY-MM-DD format)
            website: Filter by website URL (case-insensitive, partial match)

        Returns:
            List of filtered article dictionaries
        """
        articles = self.article_repo.list_articles()
        formatted_articles = self._format_articles(articles)

        # Apply search filter
        if search_query:
            formatted_articles = [
                a
                for a in formatted_articles
                if search_query in a["title"].lower()
                or search_query in a["author"].lower()
            ]

        # Apply author filter (partial match)
        if author:
            formatted_articles = [
                a for a in formatted_articles if author.lower() in a["author"].lower()
            ]

        # Apply date range filter
        if date_from or date_to:
            filtered_by_date = []
            for a in formatted_articles:
                article_date = a["date"]
                if article_date == "N/A":
                    continue

                if date_from and article_date < date_from:
                    continue
                if date_to and article_date > date_to:
                    continue

                filtered_by_date.append(a)
            formatted_articles = filtered_by_date

        # Apply website filter (partial match)
        if website:
            formatted_articles = [
                a
                for a in formatted_articles
                if website.lower() in a["website_url"].lower()
            ]

        return formatted_articles

    def get_filter_options(self) -> Dict:
        """
        Get available filter options for articles.

        Returns:
            Dictionary containing min/max dates for range picker
        """
        articles = self.article_repo.list_articles()
        formatted_articles = self._format_articles(articles)

        # Extract date range
        valid_dates = [a["date"] for a in formatted_articles if a["date"] != "N/A"]

        if valid_dates:
            min_date = min(valid_dates)
            max_date = max(valid_dates)
        else:
            min_date = ""
            max_date = ""

        return {
            "min_date": min_date,
            "max_date": max_date,
        }

    def clear_all_articles(self) -> int:
        """
        Delete all articles from database.

        Returns:
            Number of articles deleted
        """
        articles = self.article_repo.list_articles()
        deleted_count = 0

        for article in articles:
            if self.article_repo.delete_article(article.article_id):
                deleted_count += 1

        return deleted_count

    def get_article_stats(self) -> Dict:
        """
        Get statistics about articles in database.

        Returns:
            Dictionary with article statistics
        """
        articles = self.article_repo.list_articles()

        # Count unique authors
        unique_authors = set()
        for article in articles:
            if article.author:
                unique_authors.add(article.author.name)

        return {
            "total_articles": len(articles),
            "unique_authors": len(unique_authors),
            "authors": list(unique_authors),
        }

    @staticmethod
    def _format_articles(articles) -> List[Dict]:
        """
        Format articles for JSON serialization.

        Args:
            articles: List of Article ORM objects

        Returns:
            List of formatted article dictionaries
        """
        articles_data = []
        for article in articles:
            # Extract website URL from article URL
            parsed_url = urlparse(article.url)
            website_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            articles_data.append(
                {
                    "id": article.article_id,
                    "title": article.title,
                    "author": article.author.name if article.author else "Unknown",
                    "url": article.url,
                    "website_url": website_url,
                    "date": article.publication_date.isoformat()
                    if article.publication_date
                    else "N/A",
                }
            )
        return articles_data
