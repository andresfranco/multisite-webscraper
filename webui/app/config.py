"""
Flask Application Configuration
================================
Configuration settings for different environments (development, testing, production).
"""

import os
from pathlib import Path


class Config:
    """Base configuration for all environments."""

    # Application Settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Database Settings
    BASE_DIR = Path(__file__).parent.parent.parent
    DB_PATH = str(BASE_DIR / "scraper_data.db")

    # Scraping Settings
    SUPPORTED_URLS = [
        "https://realpython.com/",
        "https://www.freecodecamp.org/news",
        "https://www.datacamp.com/blog",
    ]

    # API Settings
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True
    DB_PATH = str(Config.BASE_DIR / "tests" / "test_scraper.db")
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False


def get_config():
    """
    Get configuration based on environment.

    Returns:
        Config: Configuration class for the current environment
    """
    env = os.environ.get("FLASK_ENV", "development").lower()

    config_mapping = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = config_mapping.get(env, DevelopmentConfig)

    # Validate production configuration
    if config_class == ProductionConfig:
        if not os.environ.get("SECRET_KEY"):
            raise ValueError(
                "SECRET_KEY environment variable must be set in production"
            )

    return config_class
