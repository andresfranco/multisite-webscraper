"""
Routes Package
==============
Blueprint modules for Flask application routes.
"""

from .api import api_bp
from .pages import pages_bp

__all__ = ["api_bp", "pages_bp"]
