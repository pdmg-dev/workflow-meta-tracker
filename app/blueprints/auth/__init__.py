from flask import Blueprint

from . import views  # noqa: F401

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
