# app/blueprints/admin/views.py
from flask import render_template
from flask_login import login_required

from . import staff_bp


@staff_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("staff/dashboard.html")
