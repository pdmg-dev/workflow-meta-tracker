# app/blueprints/auth/__init__.py
from flask import Blueprint

from app.blueprints.auth import models
from app.extensions import db, login_manager

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


from . import forms, views  # noqa: F401 E402


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(models.AuthIdentity, int(user_id))
