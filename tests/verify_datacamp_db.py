#!/usr/bin/env python3
"""
Verify that DataCamp articles were successfully saved to the database.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.database import create_connection, create_tables
from webscraper_core.repositories.article_repository import ArticleRepository
from webscraper_core.repositories.author_repository import AuthorRepository


def main():
    """Verify database contents for DataCamp articles."""

    print("=" * 80)
    print("Database Verification - DataCamp Articles")
    print("=" * 80)
    print(f"\nVerification at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Initialize database
        db_path = str(Path(__file__).parent.parent / "scraper_data.db")
        SessionLocal = create_connection(db_path)
        if SessionLocal is None:
            print("❌ Failed to connect to database")
            return 1

        create_tables()
        session = SessionLocal()

        # Initialize repositories
        article_repo = ArticleRepository(session)
        author_repo = AuthorRepository(session)

        # Get all articles
        all_articles = article_repo.list_articles()

        print(f"📊 TOTAL ARTICLES IN DATABASE: {len(all_articles)}")

        # Count articles by source (inferred from author)
        datacamp_articles = []
        freecodecamp_articles = []
        realpython_articles = []

        for article in all_articles:
            # Simple heuristic: try to find articles from DataCamp by URL
            if "datacamp.com" in article.url:
                datacamp_articles.append(article)
            elif "freecodecamp.org" in article.url:
                freecodecamp_articles.append(article)
            elif "realpython.com" in article.url:
                realpython_articles.append(article)

        print(f"\n📈 ARTICLES BY SOURCE:")
        print(f"  DataCamp: {len(datacamp_articles)}")
        print(f"  FreeCodeCamp: {len(freecodecamp_articles)}")
        print(f"  Real Python: {len(realpython_articles)}")

        # Display DataCamp articles
        if datacamp_articles:
            print("\n" + "=" * 80)
            print("DATACAMP ARTICLES IN DATABASE")
            print("=" * 80)

            for i, article in enumerate(datacamp_articles, 1):
                author = (
                    session.query(AuthorRepository(session).model)
                    .filter(
                        AuthorRepository(session).model.author_id == article.author_id
                    )
                    .first()
                )
                author_name = author.name if author else "Unknown"

                print(f"\n[{i}] {article.title}")
                print(f"    Author: {author_name}")
                print(f"    Date: {article.publication_date}")
                print(f"    URL: {article.url[:70]}...")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ DataCamp articles successfully saved: {len(datacamp_articles)}")
        print(f"Total articles in database: {len(all_articles)}")

        session.close()
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
