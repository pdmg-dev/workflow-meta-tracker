# app/blueprints/__init__.py
from .admin import admin_bp
from .auth import auth_bp
from .tracker import tracker_bp
from .voucher import voucher_bp

__all__ = ["auth_bp", "tracker_bp", "admin_bp", "voucher_bp"]
