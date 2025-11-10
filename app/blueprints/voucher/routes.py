# app/blueprints/vouchers/routes.py
from zoneinfo import ZoneInfo

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.voucher.services import create_voucher, get_todays_vouchers, update_voucher
from app.extensions import db
from app.models.user import Role
from app.models.voucher import Voucher, VoucherStatusHistory, VoucherStatusTransition
from app.utils.access_control import require_roles

from . import voucher_bp
from .forms import DVNumberForm, RemarksForm, VoucherForm


@voucher_bp.route("/voucher/new", methods=["GET", "POST"])
@login_required
@require_roles("admin", "encoder")
def new_voucher():
    vouchers = get_todays_vouchers()
    form = VoucherForm()
    if request.method == "POST":
        if form.validate_on_submit():
            voucher = create_voucher(form, current_user)
            form = VoucherForm(formdata=None)
            flash("Voucher added successfully", "success")
            return render_template("voucher/fragments/new.html", vouchers=vouchers, form=form, voucher=voucher)
        return render_template("voucher/forms/entry.html", form=form)
    # For the cancel button
    if request.headers.get("HX-Request") == "true":
        return render_template("voucher/forms/entry.html", form=form)
    return render_template("voucher/new.html", vouchers=vouchers, form=form, mode="new")


@voucher_bp.route("/voucher/<int:voucher_id>/edit", methods=["GET", "POST"])
@login_required
@require_roles("admin", "encoder")
def edit_voucher(voucher_id):
    voucher = Voucher.query.get(voucher_id)
    vouchers = get_todays_vouchers()
    form = VoucherForm(obj=voucher)
    if request.method == "POST":
        if form.validate_on_submit():
            update_voucher(voucher, form, current_user)
            flash("Voucher updated successfully.", "success")
            return render_template("voucher/fragments/edit.html", vouchers=vouchers, form=form, voucher=voucher)
        return render_template("voucher/forms/edit.html", form=form)

    form.date_received.data = (
        voucher.date_received.replace(tzinfo=ZoneInfo("UTC"))
        .astimezone(ZoneInfo("Asia/Manila"))
        .strftime("%m/%d/%Y %I:%M %p")
    )
    form.voucher_type.data = voucher.voucher_type.id
    form.origin_id.data = voucher.origin.id
    form.origin.data = voucher.origin.keyword or voucher.origin.name
    return render_template("voucher/edit.html", form=form, voucher=voucher, vouchers=vouchers, mode="edit")


@voucher_bp.route("/voucher/<int:voucher_id>/edit-form")
@login_required
@require_roles("admin", "encoder")
def edit_voucher_form(voucher_id):
    voucher = Voucher.query.get(voucher_id)
    form = VoucherForm(obj=voucher)
    form.date_received.data = (
        voucher.date_received.replace(tzinfo=ZoneInfo("UTC"))
        .astimezone(ZoneInfo("Asia/Manila"))
        .strftime("%m/%d/%Y %I:%M %p")
    )
    form.voucher_type.data = voucher.voucher_type.id
    form.origin_id.data = voucher.origin.id
    form.origin.data = voucher.origin.keyword or voucher.origin.name
    return render_template("voucher/forms/edit.html", form=form, voucher=voucher)


@voucher_bp.route("/voucher/<int:voucher_id>/preview")
@login_required
@require_roles("admin", "encoder")
def preview_voucher(voucher_id):
    voucher = Voucher.query.get(voucher_id)
    return render_template("voucher/fragments/preview.html", voucher=voucher)


@voucher_bp.route("/voucher/<int:voucher_id>/history")
@login_required
def status_history(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    if not voucher:
        return "", 204
    history = voucher.history.order_by(VoucherStatusHistory.updated_at.desc()).all()
    return render_template("voucher/fragments/history.html", voucher=voucher, history=history)


@voucher_bp.route("/voucher/<int:voucher_id>/particulars")
@login_required
def particulars(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    return render_template("voucher/fragments/particulars.html", voucher=voucher)


@voucher_bp.route("/voucher/bulk-update", methods=["POST"])
@login_required
def bulk_update_status():
    ids = request.form.getlist("voucher_ids")
    if not ids:
        return "", 204

    explicit_code = request.form.get("target_status") or request.args.get("target")
    user_role_ids = {r.id for r in current_user.roles}

    allowed_transitions = (
        db.session.query(VoucherStatusTransition)
        .join(VoucherStatusTransition.allowed_roles)
        .filter(Role.id.in_(user_role_ids))
        .all()
    )

    trans_map = {}
    for t in allowed_transitions:
        trans_map.setdefault(t.from_status_id, []).append(t)

    updated_vouchers = []
    for v in Voucher.query.filter(Voucher.id.in_(ids)).all():
        next_t = None
        if explicit_code:
            next_t = next(
                (t for t in trans_map.get(v.status_id, []) if t.to_status.code == explicit_code),
                None,
            )
        else:
            possible = trans_map.get(v.status_id, [])
            next_t = possible[0] if possible else None

        if not next_t:
            continue

        v.status = next_t.to_status
        v.updated_by_id = current_user.id
        db.session.add(
            VoucherStatusHistory(
                voucher=v,
                status=next_t.to_status,
                updated_by_id=current_user.id,
                remarks=next_t.to_status.remarks,
            )
        )
        updated_vouchers.append(v)

    if not updated_vouchers:
        return "", 204

    db.session.commit()

    payload = {
        "updated": [
            {
                "id": v.id,
                "status": v.status.name,
                "code": v.status.code,
                "updated_at": v.updated_at.replace(tzinfo=ZoneInfo("UTC"))
                .astimezone(ZoneInfo("Asia/Manila"))
                .strftime("%m-%d %I:%M %p"),
            }
            for v in updated_vouchers
        ]
    }

    return jsonify(payload)


@voucher_bp.route("/voucher/<int:voucher_id>/return", methods=["GET", "POST"])
@login_required
def mark_as_returned(voucher_id):
    form = RemarksForm()
    voucher = Voucher.query.get_or_404(voucher_id)

    if request.method == "POST" and form.validate_on_submit():
        user_role_ids = {r.id for r in current_user.roles}

        allowed_transitions = (
            db.session.query(VoucherStatusTransition)
            .join(VoucherStatusTransition.allowed_roles)
            .filter(Role.id.in_(user_role_ids))
            .all()
        )

        next_transition = next(
            (
                t
                for t in allowed_transitions
                if t.from_status_id == voucher.status_id and t.to_status.code == "returned"
            ),
            None,
        )

        if not next_transition:
            return render_template(
                "voucher/forms/remarks.html",
                voucher=voucher,
                form=form,
                modal_title="Mark as Returned",
            )

        voucher.status = next_transition.to_status
        voucher.updated_by_id = current_user.id

        history = VoucherStatusHistory(
            voucher=voucher,
            status=next_transition.to_status,
            updated_by_id=current_user.id,
            remarks=form.remarks.data,
        )

        db.session.add_all([voucher, history])
        db.session.commit()

        # Detect HTMX JSON request
        if request.accept_mimetypes.accept_json:
            return jsonify(
                {
                    "updated": [
                        {
                            "id": voucher.id,
                            "status": voucher.status.name,
                            "code": voucher.status.code,
                            "updated_at": voucher.updated_at.replace(tzinfo=ZoneInfo("UTC"))
                            .astimezone(ZoneInfo("Asia/Manila"))
                            .strftime("%m-%d %I:%M %p"),
                        }
                    ]
                }
            )

        flash("Voucher marked as returned.", "success")
        return redirect(url_for("voucher_bp.view_voucher", voucher_id=voucher.id))

    # ---- GET request (open modal)
    return render_template(
        "voucher/forms/remarks.html",
        voucher=voucher,
        form=form,
        modal_title="Mark as Returned",
    )


@voucher_bp.route("/voucher/serial")
def dv_number():
    form = DVNumberForm()
    return render_template("voucher/forms/dv_number.html", form=form)
