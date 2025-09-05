# app/blueprints/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from . import forms, views  # noqa: F401 E402
