import requests
from pathlib import Path
from .scraper import WebScraper
from .scrapers.realpython_scraper import RealPythonScraper
from .scrapers.freecodecamp_scraper import FreeCodeCampScraper
from .scrapers.datacamp_scraper import DataCampScraper
from .analyzer import process_titles
from .database import create_connection, create_tables
from .repositories.author_repository import AuthorRepository
from .repositories.article_repository import ArticleRepository
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict, Optional
from collections import Counter

# Database path pointing to root folder
DB_PATH = str(Path(__file__).parent.parent / "scraper_data.db")


def _get_scraper_for_url(url: str) -> WebScraper:
    """Get the appropriate scraper class for a given URL.

    Args:
        url: The URL to scrape

    Returns:
        An instance of the appropriate scraper class
    """
    if "realpython.com" in url:
        return RealPythonScraper(url)
    elif "freecodecamp.org" in url:
        return FreeCodeCampScraper(url)
    elif "datacamp.com" in url:
        return DataCampScraper(url)
    else:
        # Fallback to generic WebScraper
        return WebScraper(url)


def run(url: str):
    """Run scraper for single URL, extract data, and save to database."""
    scraper = _get_scraper_for_url(url)

    # Use the scraper's fetch_page method instead of basic requests.get
    # This allows specialized scrapers (like DataCampScraper) to use their own methods
    html_content = scraper.fetch_page()
    if not html_content:
        print(f"Failed to fetch {url}")
        return

    articles = scraper.extract_article_data(html_content)
    if not articles:
        print("Failed to extract articles from the response.")
        return

    # Save articles to database
    result = _save_articles_to_db(articles, url)

    # Display results
    print(f"\nProcessed: {url}")
    print(f"  Created: {result['created']}")
    print(f"  Skipped: {result['skipped']}")
    if result["errors"]:
        print(f"  Errors: {result['errors']}")


def _save_articles_to_db(articles: List[dict], url: str, session) -> Dict:
    """Save scraped articles to the database.

    Args:
        articles: List of article dictionaries from scraper
        url: Source URL (for tracking)
        session: Database session (shared across worker threads)

    Returns:
        Dictionary with statistics: {created, skipped, errors}
    """
    try:
        # Initialize repositories with the provided session
        author_repo = AuthorRepository(session)
        article_repo = ArticleRepository(session)

        # Initialize scraper for fetching additional data if needed
        scraper = WebScraper(url)

        created = 0
        skipped = 0
        errors = 0

        # Process each article
        for article_data in articles:
            try:
                # For Real Python articles, try to fetch author from article detail page
                # Fetch for ALL unknown authors (not just the first few)
                if "realpython.com" in url and article_data.get("author") == "Unknown":
                    article_url = article_data.get("url", "")
                    if article_url:
                        fetched_author = scraper.fetch_realpython_author(article_url)
                        if fetched_author:
                            article_data["author"] = fetched_author

                # Get or create author
                author_name = article_data.get("author", "Unknown")
                author = author_repo.get_or_create(author_name)

                if not author:
                    errors += 1
                    continue

                # Try to add article (will skip if URL already exists)
                result = article_repo.add_article_with_dedup(article_data, author)

                if result:
                    created += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"Error processing article: {e}")
                errors += 1
                continue

        return {"created": created, "skipped": skipped, "errors": errors}

    except Exception as e:
        print(f"Database error: {e}")
        return {"created": 0, "skipped": 0, "errors": len(articles)}


def _process_single(url: str, session) -> Dict:
    """Helper that scrapes URL, extracts articles, and saves to database.

    Args:
        url: URL to process
        session: Database session (shared across worker threads)

    Returns dictionary with statistics and metadata.
    """
    try:
        scraper = _get_scraper_for_url(url)
        # Use the scraper's fetch_page method instead of basic requests.get
        # This allows specialized scrapers (like DataCampScraper) to use their own methods
        html_content = scraper.fetch_page()
        if not html_content:
            return {
                "url": url,
                "status": "error",
                "message": f"Failed to fetch content",
                "created": 0,
                "skipped": 0,
                "errors": 1,
            }
    except Exception as err:
        return {
            "url": url,
            "status": "error",
            "message": f"Failed to fetch: {err}",
            "created": 0,
            "skipped": 0,
            "errors": 1,
        }

    try:
        articles = scraper.extract_article_data(html_content)
        if not articles:
            return {
                "url": url,
                "status": "error",
                "message": "Failed to extract articles",
                "created": 0,
                "skipped": 0,
                "errors": 1,
            }

        # Save to database using shared session
        result = _save_articles_to_db(articles, url, session)

        return {
            "url": url,
            "status": "success",
            "created": result["created"],
            "skipped": result["skipped"],
            "errors": result["errors"],
            "total_articles": result["created"] + result["skipped"],
        }

    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "message": str(e),
            "created": 0,
            "skipped": 0,
            "errors": 1,
        }


def run_many(urls: List[str], max_workers: int = 5) -> List[Dict]:
    """Run scrape and save in parallel for a list of URLs using threads.

    Creates a single database session and shares it with all worker threads.

    Returns a list of result dictionaries with statistics.
    """
    # Initialize database once for all workers
    SessionLocal = create_connection(DB_PATH)
    if SessionLocal is None:
        print("Failed to create database connection")
        return []

    create_tables()
    session = SessionLocal()

    try:
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            # Pass the shared session to each worker
            future_to_url = {
                ex.submit(_process_single, url, session): url for url in urls
            }
            for fut in as_completed(future_to_url):
                url = future_to_url[fut]
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as exc:
                    results.append(
                        {
                            "url": url,
                            "status": "error",
                            "message": str(exc),
                            "created": 0,
                            "skipped": 0,
                            "errors": 1,
                        }
                    )
        return results
    finally:
        # Close session after all workers are done
        session.close()


def aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate statistics from multiple results.

    Args:
        results: List of result dictionaries from run_many()

    Returns:
        Dictionary with aggregated statistics
    """
    total_created = 0
    total_skipped = 0
    total_errors = 0
    successful_urls = 0
    failed_urls = 0

    for result in results:
        if result["status"] == "success":
            successful_urls += 1
            total_created += result.get("created", 0)
            total_skipped += result.get("skipped", 0)
        else:
            failed_urls += 1
            total_errors += result.get("errors", 1)

    return {
        "total_urls": len(results),
        "successful_urls": successful_urls,
        "failed_urls": failed_urls,
        "total_created": total_created,
        "total_skipped": total_skipped,
        "total_errors": total_errors,
    }


def run_many_and_aggregate(
    urls: List[str], max_workers: int = 5
) -> Tuple[List[Dict], Dict]:
    """Convenience: run many URLs in parallel and return aggregated statistics.

    Returns (results, aggregated_stats)
    """
    results = run_many(urls, max_workers=max_workers)
    stats = aggregate_results(results)
    return results, stats
