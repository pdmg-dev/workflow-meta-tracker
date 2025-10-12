# app/blueprints/dashboard/views.py
from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

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
        "dashboard.html", all_vouchers=Voucher.query, voucher_status=voucher_status, vouchers=vouchers
    )


@tracker_bp.route("/vouchers", methods=["GET"])
@login_required
def view_vouchers():
    # Check if user has the 'encoder' role
    role_map = ["admin", "encoder"]
    is_admin_or_encoder = any(role.code in role_map for role in current_user.roles)
    if is_admin_or_encoder:
        vouchers = Voucher.query.all()
    else:
        allowed_type_ids = [vt.id for vt in current_user.voucher_types]
        vouchers = Voucher.query.filter(Voucher.voucher_type_id.in_(allowed_type_ids)).all()

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

    return render_template("vouchers.html", vouchers=vouchers)
