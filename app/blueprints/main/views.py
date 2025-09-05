# app/blueprints/main/views.py
from flask import redirect, url_for
from flask_login import current_user

from app.utils.routing import redirect_to_dashboard

from . import main_bp


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
    return redirect(url_for("auth.login"))
