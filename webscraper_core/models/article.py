"""Article model using SQLAlchemy."""
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base

class Article(Base):
    """Article model for the database."""
    __tablename__ = 'article'
    
    article_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey('author.author_id'), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    publication_date = Column(Date, nullable=True)

    # Relationship to Author model
    author = relationship("Author", back_populates="articles")
    
    def __repr__(self):
        return f"<Article(article_id={self.article_id}, author_id={self.author_id}, title='{self.title}', url='{self.url}', date={self.publication_date})>"
