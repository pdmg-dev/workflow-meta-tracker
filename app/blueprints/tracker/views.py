# app/blueprints/dashboard/views.py
from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.voucher import Voucher

from . import tracker_bp


@tracker_bp.route("/")
@login_required
def index():
    role_codes = {role.code.lower() for role in current_user.roles if role.code}

    if "admin" in role_codes:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("tracker.dashboard"))


@tracker_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    vouchers = db.session.query(Voucher).order_by(Voucher.date_received.desc())
    return render_template("dashboard.html", vouchers=vouchers)


@tracker_bp.route("/vouchers", methods=["GET"])
@login_required
def view_vouchers():
    vouchers = Voucher.query.order_by(Voucher.date_received.desc()).all()
    return render_template("vouchers.html", vouchers=vouchers)
