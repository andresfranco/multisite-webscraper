"""
API Routes
==========
Blueprint for API endpoints handling scraping and article operations.
"""

from flask import Blueprint, request, jsonify, g
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
    # Store session in g for cleanup after request
    if not hasattr(g, "db_sessions"):
        g.db_sessions = []
    g.db_sessions.append(session)
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
    API endpoint to fetch articles from database with filtering and pagination.

    Query Parameters:
        - search: Search term for title/author (optional)
        - author: Filter by author name (optional, partial match)
        - website: Filter by website URL (optional, partial match)
        - date_from: Start date for date range filter (YYYY-MM-DD, optional)
        - date_to: End date for date range filter (YYYY-MM-DD, optional)
        - page: Page number (default: 1)
        - per_page: Items per page - 5, 10, or 20 (default: 10)

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Get query parameters
        search_query = request.args.get("search", "").strip().lower()
        author_filter = request.args.get("author", "").strip()
        website_filter = request.args.get("website", "").strip()
        date_from = request.args.get("date_from", "").strip()
        date_to = request.args.get("date_to", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page not in [5, 10, 20]:
            per_page = 10

        scraper_service = get_scraper_service(db_service)

        # Get filtered articles
        filtered_articles = scraper_service.get_filtered_articles(
            search_query=search_query,
            author=author_filter,
            date_from=date_from,
            date_to=date_to,
            website=website_filter,
        )

        # Calculate pagination
        total_count = len(filtered_articles)
        total_pages = (total_count + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_articles = filtered_articles[start_idx:end_idx]

        return (
            jsonify(
                {
                    "success": True,
                    "articles": paginated_articles,
                    "count": len(paginated_articles),
                    "total_count": total_count,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
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


@api_bp.route("/article-filters", methods=["GET"])
def get_article_filters(db_service: DatabaseService) -> Tuple[dict, int]:
    """
    API endpoint to fetch available filter options.

    Args:
        db_service: DatabaseService instance (injected via before_request)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        scraper_service = get_scraper_service(db_service)
        filters = scraper_service.get_filter_options()

        return (
            jsonify(
                {
                    "success": True,
                    "filters": filters,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error fetching filters: {str(e)}"}),
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
