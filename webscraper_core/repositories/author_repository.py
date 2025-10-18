# AuthorRepository class to manage author data
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import Author
from .base_repository import BaseRepository
class AuthorRepository(BaseRepository):
    """Repository class for managing Author data in the database."""

    def __init__(self, session: Session):
        super().__init__(session, Author)

    def get_by_name(self, name: str) -> Optional[Author]:
        """Retrieve an author by their name."""
        try:
            return self.session.query(self.model).filter(self.model.name == name).first()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return None

    def get_or_create(self, name: str) -> Optional[Author]:
        """Get existing author by name or create new one if not exists.
        
        This method prevents duplicate authors in the database.
        """
        try:
            # First, try to get existing author
            author = self.get_by_name(name)
            if author:
                return author
            
            # If not found, create new author
            return self.create_author(name)
        except SQLAlchemyError as e:
            print(f"Database error in get_or_create: {e}")
            return None
    def create_author(self, name: str) -> Optional[Author]:
        """Create a new author in the database."""
        try:
            new_author = Author(name=name)
            self.session.add(new_author)
            self.session.commit()
            return new_author
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to create author: {e}")
            return None
    def list_authors(self) -> List[Author]:
        """List all authors in the database."""
        try:
            return self.session.query(self.model).all()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return []   
    def delete_author(self, author_id: int) -> bool:
        """Delete an author by their ID."""
        try:
            author = self.session.query(self.model).get(author_id)
            if author:
                self.session.delete(author)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to delete author: {e}")
            return False
    def update_author(self, author_id: int, name: str) -> Optional[Author]:
        """Update an author's name by their ID."""
        try:
            author = self.session.query(self.model).get(author_id)
            if author:
                author.name = name
                self.session.commit()
                return author
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to update author: {e}")
            return None
        