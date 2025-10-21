#!/usr/bin/env python
"""
Run script for the Flask Web Scraper Application.

This script provides a convenient way to start the Flask application
with proper configuration and error handling.

Usage:
    python run.py                    # Start in development mode
    python run.py --production       # Start in production mode
    python run.py --help            # Show help message
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import webscraper_core
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app


def print_banner():
    """Print ASCII banner."""
    banner = """
    ╔════════════════════════════════════════════════════╗
    ║   📰 Multisite Web Scraper - Flask Application    ║
    ║                                                    ║
    ║   A modern web interface for scraping and         ║
    ║   displaying articles from multiple tech sites    ║
    ╚════════════════════════════════════════════════════╝
    """
    print(banner)


def print_welcome(mode, host, port, db_path):
    """Print welcome message with startup information."""
    print("\n✨ Starting Flask Web Scraper Application...\n")
    print(f"📋 Mode:          {mode}")
    print(f"🌐 Host:          {host}")
    print(f"🔌 Port:          {port}")
    print(f"💾 Database:      {db_path}")
    print("\n" + "=" * 50)
    print("🚀 Application Ready!")
    print("=" * 50)
    print(f"\n🔗 Open your browser and go to:")
    print(f"   👉 http://{host}:{port}/")
    print(f"\n📊 View grid:     http://{host}:{port}/grid")
    print("\n💡 Tips:")
    print("   - Select URLs to scrape on the home page")
    print("   - Click 'Start Scraping' to begin")
    print("   - View results in the grid view")
    print("   - Use Ctrl+C to stop the server")
    print("\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Flask Web Scraper Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Development mode (auto-reload)
  python run.py --production       # Production mode
  python run.py --host 0.0.0.0     # Listen on all interfaces
  python run.py --port 8080        # Use custom port
        """,
    )

    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (no auto-reload, no debugger)",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port", type=int, default=5000, help="Port number (default: 5000)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker threads for production mode (default: 4)",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Create Flask app
    try:
        if args.production:
            os.environ["FLASK_ENV"] = "production"
            app = create_app("production")
        else:
            os.environ["FLASK_ENV"] = "development"
            app = create_app("development")
    except Exception as e:
        print(f"\n❌ Failed to create application: {e}")
        sys.exit(1)

    # Determine mode
    mode = "Production" if args.production else "Development"
    db_path = app.config.get("DB_PATH", "Unknown")

    # Print welcome message
    print_welcome(mode, args.host, args.port, db_path)

    # Run Flask app
    try:
        if args.production:
            # Production mode using Gunicorn would be better, but we'll use basic mode
            print(
                "⚠️  For true production, use: gunicorn -w 4 -b 0.0.0.0:5000 app:app\n"
            )
            app.run(host=args.host, port=args.port, debug=False, threaded=True)
        else:
            # Development mode with auto-reload and debugger
            app.run(
                host=args.host,
                port=args.port,
                debug=True,
                use_reloader=True,
                use_debugger=True,
            )

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        print("✅ Application stopped")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
