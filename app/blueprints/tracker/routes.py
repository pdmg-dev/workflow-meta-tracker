# app/blueprints/dashboard/views.py

from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models.voucher import Voucher, VoucherStatus

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
    # Check if user has the 'encoder' role
    role_map = ["admin", "encoder"]
    is_admin_or_encoder = any(role.code in role_map for role in current_user.roles)

    if is_admin_or_encoder:
        vouchers = Voucher.query.all()
    else:
        user_voucher_types = [voucher_type.id for voucher_type in current_user.voucher_types]
        print(user_voucher_types)
        vouchers = Voucher.query.filter(Voucher.voucher_type_id.in_(user_voucher_types)).all()

    # Sort vouchers by reference number
    vouchers = sorted(
        vouchers,
        key=lambda v: (
            int(v.reference_number[1:3]),  # year
            int(v.reference_number[3:5]),  # month
            int(v.reference_number[5:]),  # sequence
        ),
        reverse=True,
    )

    received_vouchers = Voucher.query.join(Voucher.status).filter(VoucherStatus.code == "received")
    checked_vouchers = Voucher.query.join(Voucher.status).filter(VoucherStatus.code == "checked")
    sorted_vouchers = Voucher.query.join(Voucher.status).filter(VoucherStatus.code == "sorted")
    approved_vouchers = Voucher.query.join(Voucher.status).filter(VoucherStatus.code == "approved")

    pending = sum([received_vouchers.count(), checked_vouchers.count(), sorted_vouchers.count()])

    voucher_status = {
        "received": received_vouchers,
        "checked": checked_vouchers,
        "sorted": sorted_vouchers,
        "approved": approved_vouchers,
        "pending": pending,
    }

    return render_template(
        "dashboard.html",
        all_vouchers=Voucher.query,
        voucher_status=voucher_status,
        vouchers=vouchers,
    )


@tracker_bp.route("/vouchers", methods=["GET"])
@login_required
def view_vouchers():
    page = request.args.get("page", 1, type=int)
    per_page = 15  # adjust as you like

    role_map = ["admin", "encoder"]
    is_admin_or_encoder = any(role.code in role_map for role in current_user.roles)
    query = Voucher.query

    if not is_admin_or_encoder:
        allowed_type_ids = [vt.id for vt in current_user.voucher_types]
        query = query.filter(Voucher.voucher_type_id.in_(allowed_type_ids))

    # Apply sorting dynamically (if needed)
    sort_col = request.args.get("sort", "reference_number")
    sort_dir = request.args.get("dir", "desc")
    if sort_col and hasattr(Voucher, sort_col):
        col = getattr(Voucher, sort_col)
        query = query.order_by(col.desc() if sort_dir == "desc" else col.asc())

    vouchers = query.paginate(page=page, per_page=per_page, error_out=False)

    template = "vouchers.html"
    if request.headers.get("HX-Request"):
        template = "voucher/_table.html"

    return render_template(template, vouchers=vouchers.items, pagination=vouchers)


@tracker_bp.route("/chart-data")
@login_required
def chart_data():

    status_counts = (
        db.session.query(VoucherStatus.code, func.count(Voucher.id)).join(Voucher).group_by(VoucherStatus.code).all()
    )

    return jsonify(dict(status_counts))
