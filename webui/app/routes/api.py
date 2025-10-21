"""
API Routes
==========
Blueprint for API endpoints handling scraping and article operations.
"""

from flask import Blueprint, request, jsonify
from typing import Tuple

from ..services import ScraperService, DatabaseService
from ..config import Config

# Create blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_scraper_service(db_service: DatabaseService) -> ScraperService:
    """
    Factory function to create ScraperService instance.

    Args:
        db_service: DatabaseService instance

    Returns:
        ScraperService: Initialized scraper service
    """
    session = db_service.get_session()
    return ScraperService(session)


@api_bp.route("/scrape", methods=["POST"])
def scrape(db_service: DatabaseService) -> Tuple[dict, int]:
    """
    API endpoint to start scraping process.

    Expected JSON payload:
    {
        "urls": ["url1", "url2", ...],
        "workers": 3  (optional)
    }

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"success": False, "message": "No JSON data provided"}),
                400,
            )

        urls = data.get("urls", [])
        workers = data.get("workers", 3)

        # Validate URLs
        if not urls:
            return (
                jsonify({"success": False, "message": "No URLs provided"}),
                400,
            )

        # Filter for supported URLs
        valid_urls = [
            url
            for url in urls
            if url in Config.SUPPORTED_URLS or url.startswith("http")
        ]

        if not valid_urls:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "No valid URLs provided. Supported URLs: "
                        + ", ".join(Config.SUPPORTED_URLS),
                    }
                ),
                400,
            )

        # Run scraper
        scraper_service = get_scraper_service(db_service)
        results, stats = scraper_service.scrape_urls(valid_urls, max_workers=workers)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Scraping completed successfully",
                    "stats": stats,
                    "results": results,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "message": f"Invalid input: {str(e)}"}), 400
    except RuntimeError as e:
        return jsonify({"success": False, "message": f"Scraping error: {str(e)}"}), 500
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error during scraping: {str(e)}"}),
            500,
        )


@api_bp.route("/articles", methods=["GET"])
def get_articles(db_service: DatabaseService) -> Tuple[dict, int]:
    """
    API endpoint to fetch articles from database.

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        scraper_service = get_scraper_service(db_service)
        articles = scraper_service.get_all_articles()

        return (
            jsonify(
                {
                    "success": True,
                    "articles": articles,
                    "count": len(articles),
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error fetching articles: {str(e)}"}
            ),
            500,
        )


@api_bp.route("/clear-articles", methods=["POST"])
def clear_articles(db_service: DatabaseService) -> Tuple[dict, int]:
    """
    API endpoint to clear all articles from database.

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        scraper_service = get_scraper_service(db_service)
        deleted_count = scraper_service.clear_all_articles()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Deleted {deleted_count} articles",
                    "deleted_count": deleted_count,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error clearing articles: {str(e)}"}
            ),
            500,
        )
