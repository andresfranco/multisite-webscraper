"""
Page Routes
===========
Blueprint for rendering template pages.
"""

from flask import Blueprint, render_template

from ..services import ScraperService, DatabaseService
from ..config import Config

# Create blueprint
pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """
    Home page with URL input form.

    Returns:
        Rendered index template
    """
    return render_template("index.html", supported_urls=Config.SUPPORTED_URLS)


@pages_bp.route("/grid")
def grid(db_service: DatabaseService):
    """
    Display scraped articles in a grid.

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Rendered grid template with articles
    """
    try:
        scraper_service = ScraperService(db_service.get_session())
        articles = scraper_service.get_all_articles()
        return render_template("grid.html", articles=articles)
    except Exception as e:
        return render_template("grid.html", articles=[], error=str(e))
