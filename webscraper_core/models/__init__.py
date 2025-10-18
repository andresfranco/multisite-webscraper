"""Models package for webscraper_core.

Exports the Author and Article models and the Base declarative base.
"""

from .base import Base
from .author import Author
from .article import Article

__all__ = ['Author', 'Article', 'Base']

