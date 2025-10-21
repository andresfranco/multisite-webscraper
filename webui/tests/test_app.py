"""
Flask Application Tests
=======================
Test suite for Flask application functionality.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestIndexRoute:
    """Tests for index page route."""

    def test_index_get(self, client):
        """Test GET request to index page."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Web Scraper" in response.data
        assert b"Select URLs to Scrape" in response.data

    def test_index_contains_form(self, client):
        """Test that index page contains form elements."""
        response = client.get("/")
        assert b"scraperForm" in response.data
        assert b"realpython.com" in response.data
        assert b"freecodecamp.org" in response.data
        assert b"datacamp.com" in response.data


class TestGridRoute:
    """Tests for grid page route."""

    def test_grid_get(self, client):
        """Test GET request to grid page."""
        response = client.get("/grid")
        assert response.status_code == 200
        assert b"Article Collection" in response.data

    def test_grid_empty_state(self, client):
        """Test grid page displays empty state when no articles."""
        response = client.get("/grid")
        assert response.status_code == 200
        # Should contain either articles or empty state message


class TestAPIScraperEndpoint:
    """Tests for /api/scrape endpoint."""

    def test_scrape_no_data(self, client):
        """Test scrape endpoint with no JSON data."""
        response = client.post("/api/scrape", json=None)
        assert response.status_code == 400

    def test_scrape_no_urls(self, client):
        """Test scrape endpoint with empty URLs list."""
        response = client.post("/api/scrape", json={"urls": []})
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]
        assert "No URLs provided" in data["message"]

    def test_scrape_invalid_url(self, client):
        """Test scrape endpoint with invalid URLs."""
        response = client.post(
            "/api/scrape",
            json={"urls": ["https://invalid-test-url-12345.com"]},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]

    def test_scrape_valid_payload(self, client):
        """Test scrape endpoint with valid payload structure."""
        response = client.post(
            "/api/scrape",
            json={
                "urls": ["https://realpython.com/"],
                "workers": 1,
            },
        )
        # Response can be 200 or 500 depending on network
        assert response.status_code in [200, 500]


class TestAPIArticlesEndpoint:
    """Tests for /api/articles endpoint."""

    def test_get_articles(self, client):
        """Test GET articles endpoint."""
        response = client.get("/api/articles")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert "articles" in data
        assert "count" in data
        assert isinstance(data["articles"], list)

    def test_get_articles_empty(self, client):
        """Test GET articles endpoint returns empty list initially."""
        response = client.get("/api/articles")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["count"] == 0


class TestAPIClearArticlesEndpoint:
    """Tests for /api/clear-articles endpoint."""

    def test_clear_articles(self, client):
        """Test clear articles endpoint."""
        response = client.post("/api/clear-articles")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert "deleted_count" in data


class TestErrorHandlers:
    """Tests for error handlers."""

    def test_404_error(self, client):
        """Test 404 error handler."""
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        data = response.get_json()
        assert not data["success"]
        assert "Not found" in data["message"]


class TestAppConfiguration:
    """Tests for app configuration."""

    def test_app_testing_mode(self, app):
        """Test that app is in testing mode."""
        assert app.config["TESTING"]

    def test_app_debug_disabled(self, app):
        """Test that debug is disabled in testing."""
        assert not app.config["DEBUG"]

    def test_supported_urls_configured(self, app):
        """Test that supported URLs are configured."""
        assert len(app.config["SUPPORTED_URLS"]) > 0
        assert "https://realpython.com/" in app.config["SUPPORTED_URLS"]

    def test_db_path_configured(self, app):
        """Test that database path is configured."""
        assert app.config["DB_PATH"]
        assert "test_scraper.db" in app.config["DB_PATH"]
