#ArticleRepository class to manage article data
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session  
from sqlalchemy.exc import SQLAlchemyError
from ..models import Article
from .base_repository import BaseRepository
class ArticleRepository(BaseRepository):
    """Repository class for managing Article data in the database."""

    def __init__(self, session: Session):
        super().__init__(session, Article)

    def get_by_title(self, title: str) -> Optional[Article]:
        """Retrieve an article by its title."""
        try:
            return self.session.query(self.model).filter(self.model.title == title).first()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return None

    def get_by_url(self, url: str) -> Optional[Article]:
        """Retrieve an article by its URL."""
        try:
            return self.session.query(self.model).filter(self.model.url == url).first()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return None

    def create_article(self, author_id: int, title: str) -> Optional[Article]:
        """Create a new article in the database."""
        try:
            new_article = Article(author_id=author_id, title=title)
            self.session.add(new_article)
            self.session.commit()
            return new_article
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to create article: {e}")
            return None

    def add_article_with_dedup(self, data: dict, author) -> Optional[Article]:
        """Add article to database, skip if URL already exists (deduplication).
        
        Args:
            data: Dictionary with keys: title, url, publication_date (optional)
            author: Author object from AuthorRepository.get_or_create()
            
        Returns:
            New Article object if created, None if skipped (duplicate URL)
        """
        try:
            # Check if article with same URL already exists
            url = data.get('url')
            if not url:
                print("Warning: Article data missing 'url' field, skipping")
                return None
            
            existing_article = self.get_by_url(url)
            if existing_article:
                # URL already exists, skip this article
                return None
            
            # Create new article with all fields
            new_article = Article(
                title=data.get('title', 'Untitled'),
                author_id=author.author_id,
                url=url,
                publication_date=data.get('publication_date')
            )
            self.session.add(new_article)
            self.session.commit()
            return new_article
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to add article: {e}")
            return None

    def list_articles(self) -> List[Article]:
        """List all articles in the database."""
        try:
            return self.session.query(self.model).all()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return []

    def delete_article(self, article_id: int) -> bool:
        """Delete an article by its ID."""
        try:
            article = self.session.query(self.model).get(article_id)
            if article:
                self.session.delete(article)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to delete article: {e}")
            return False

    def update_article(self, article_id: int, title: str) -> Optional[Article]:
        """Update an article's title by its ID."""
        try:
            article = self.session.query(self.model).get(article_id)
            if article:
                article.title = title
                self.session.commit()
                return article
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to update article: {e}")
            return None