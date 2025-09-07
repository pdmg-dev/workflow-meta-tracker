# app/blueprints/documents/__init__.py
from flask import Blueprint

document_bp = Blueprint("documents", __name__, url_prefix="/documents")

from . import forms, views  # noqa: E402 F401
