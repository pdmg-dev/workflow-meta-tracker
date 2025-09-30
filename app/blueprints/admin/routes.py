# app/blueprints/admin/views.py
from flask import render_template
from flask_login import login_required

from . import admin_bp


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")
