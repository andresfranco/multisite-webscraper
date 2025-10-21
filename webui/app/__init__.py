"""
Flask Application Factory
==========================
Factory function for creating and configuring Flask application instances.
"""

import sys
from pathlib import Path
from flask import Flask, g

# Add parent directory to path to import webscraper_core
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .config import get_config
from .services import DatabaseService
from .routes import api_bp, pages_bp


def create_app(config=None):
    """
    Create and configure Flask application.

    Args:
        config: Configuration class or instance. If None, uses environment config.

    Returns:
        Flask: Configured Flask application instance
    """
    # Get configuration
    if config is None:
        config = get_config()
    elif isinstance(config, str):
        # If string is passed, get config by name
        from .config import DevelopmentConfig, TestingConfig, ProductionConfig

        config_map = {
            "development": DevelopmentConfig,
            "testing": TestingConfig,
            "production": ProductionConfig,
        }
        config = config_map.get(config, DevelopmentConfig)

    # Create Flask app
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Load configuration
    app.config.from_object(config)

    # Initialize database service
    try:
        db_service = DatabaseService(app.config["DB_PATH"])
        app.db_service = db_service
    except RuntimeError as e:
        app.logger.error(f"Failed to initialize database: {e}")
        raise

    # Register request handlers for dependency injection
    @app.before_request
    def inject_db_service():
        """Inject database service into request context."""
        g.db_service = app.db_service
        g.db_sessions = []

    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    # Update route functions to accept db_service from g
    def wrap_view_with_db(view_func):
        """Wrap view function to inject db_service."""

        def wrapper(*args, **kwargs):
            return view_func(g.db_service, *args, **kwargs)

        wrapper.__name__ = view_func.__name__
        return wrapper

    # Apply wrapper to API routes
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith("api."):
            view_func = app.view_functions[rule.endpoint]
            app.view_functions[rule.endpoint] = wrap_view_with_db(view_func)
        elif rule.endpoint == "pages.grid":
            view_func = app.view_functions[rule.endpoint]
            app.view_functions[rule.endpoint] = wrap_view_with_db(view_func)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import jsonify

        return jsonify({"success": False, "message": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        from flask import jsonify

        app.logger.error(f"Server error: {error}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    # Register teardown handler to close all database sessions
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close all database sessions on app shutdown."""
        if hasattr(g, "db_sessions"):
            for session in g.db_sessions:
                try:
                    session.close()
                except Exception as e:
                    app.logger.warning(f"Error closing database session: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
