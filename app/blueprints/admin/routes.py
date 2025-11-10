# app/blueprints/admin/views.py
from flask import render_template
from flask_login import login_required

from app.models.user import User

from . import admin_bp


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)
