# app/blueprints/staff/__init__.py
from flask import Blueprint

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")

from . import views  # noqa: F401 E402
