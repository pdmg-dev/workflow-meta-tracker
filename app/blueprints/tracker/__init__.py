# app/blueprints/dashboard/__init__.py
from flask import Blueprint

tracker_bp = Blueprint("tracker", __name__)

from . import routes  # noqa: F401 E402
