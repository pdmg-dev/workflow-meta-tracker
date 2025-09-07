# app/blueprints/main/views.py
from flask import redirect, url_for
from flask_login import current_user

from app.utils.routing import get_dashboard_url

from . import main_bp


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(get_dashboard_url)
    return redirect(url_for("auth.login"))
