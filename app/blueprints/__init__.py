# app/blueprints/__init__.py
from .admin import admin_bp
from .auth import auth_bp
from .main import main_bp
from .staff import staff_bp

__all__ = ["admin_bp", "auth_bp", "main_bp", "staff_bp"]
