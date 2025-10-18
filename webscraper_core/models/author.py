#Author model using sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Author(Base):
    """Author model for the database."""
    __tablename__ = 'author'
    
    author_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    # Relationship to Article model
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Author(author_id={self.author_id}, name='{self.name}')>"
