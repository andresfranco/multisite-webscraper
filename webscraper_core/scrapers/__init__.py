"""Specialized scraper classes for different websites."""
from .realpython_scraper import RealPythonScraper
from .freecodecamp_scraper import FreeCodeCampScraper
from .datacamp_scraper import DataCampScraper

__all__ = ['RealPythonScraper', 'FreeCodeCampScraper', 'DataCampScraper']
