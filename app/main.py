"""
Shortcut import for the main FastAPI application.
Allows using 'app.main:app' instead of 'app.presentacion.api_rest.main:app'
"""
from app.presentacion.api_rest.main import app

__all__ = ['app']
