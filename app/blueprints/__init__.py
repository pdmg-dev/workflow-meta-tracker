# app/blueprints/__init__.py
from .admin import admin_bp
from .auth import auth_bp
from .documents import document_bp
from .main import main_bp
from .staff import staff_bp

__all__ = ["main_bp", "auth_bp", "staff_bp", "admin_bp", "document_bp"]
