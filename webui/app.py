"""
Flask Application Entry Point
==============================
Main application module using the factory pattern.
"""

import sys
from pathlib import Path

# Add parent directory to path to import webscraper_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app

# Create Flask application
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
