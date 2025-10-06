# app/blueprints/vouchers/routes.py
from zoneinfo import ZoneInfo

from flask import flash, json, make_response, render_template, request
from flask_login import current_user, login_required

from app.blueprints.voucher.services import create_voucher, get_todays_vouchers, update_voucher
from app.extensions import db
from app.models.user import Role
from app.models.voucher import Voucher, VoucherStatusHistory, VoucherStatusTransition
from app.utils.access_control import require_roles

from . import voucher_bp
from .forms import VoucherForm


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
    return render_template("voucher/new.html", vouchers=vouchers, form=form)


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
            return render_template("voucher/fragments/new.html", vouchers=vouchers, form=form, voucher=voucher)
        return render_template("voucher/forms/entry.html", form=form)
    return render_template("voucher/edit.html", form=form, voucher=voucher, vouchers=vouchers)


@voucher_bp.route("/voucher/<int:voucher_id>/form")
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
    return render_template("voucher/forms/entry.html", form=form, voucher=voucher)


@voucher_bp.route("/voucher/<int:voucher_id>/preview")
@login_required
def preview_voucher(voucher_id):
    voucher = Voucher.query.get(voucher_id)
    return render_template("voucher/fragments/preview.html", voucher=voucher)


@voucher_bp.route("/voucher/history/<int:voucher_id>")
@login_required
def status_history(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    if not voucher:
        return "", 204
    history = voucher.history.order_by(VoucherStatusHistory.updated_at.desc()).all()
    return render_template("voucher/_history.html", voucher=voucher, history=history)


@voucher_bp.route("/voucher/bulk-update", methods=["POST"])
@login_required
def bulk_update_status():
    ids = request.form.getlist("voucher_ids")
    if not ids:
        return "No IDs selected", 204

    # if manager clicked a “Return” button you can pass ?target=returned
    explicit_code = request.form.get("target_status") or request.args.get("target")

    # Preload a list of allowed transitions for the current user
    user_role_ids = {role.id for role in current_user.roles}
    allowed_transitions = (
        db.session.query(VoucherStatusTransition)
        .join(VoucherStatusTransition.allowed_roles)
        .filter(Role.id.in_(user_role_ids))
        .all()
    )

    # Build lookup: {from_status_id: [transition objects]}
    trans_map = {}
    for t in allowed_transitions:
        trans_map.setdefault(t.from_status_id, []).append(t)

    updated = 0
    for v in Voucher.query.filter(Voucher.id.in_(ids)).all():
        next_t = None

        if explicit_code:
            # explicit target (e.g. "returned")
            next_t = next(
                (t for t in trans_map.get(v.status_id, []) if t.to_status.code == explicit_code),
                None,
            )
        else:
            # normal forward step: just pick the first allowed forward move
            # (if multiple, pick the one with the lowest id or add custom logic)
            possible = trans_map.get(v.status_id, [])
            next_t = possible[0] if possible else None

        if not next_t:
            continue  # no valid transition for this voucher/user

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
        updated += 1

    if not updated:
        return "", 204

    db.session.commit()

    response = make_response(
        render_template(
            "voucher/_table.html",
            vouchers=Voucher.query.order_by(Voucher.date_received.desc()).all(),
        )
    )
    response.headers["HX-Trigger"] = json.dumps({"bulkUpdated": {"message": f"{updated} voucher(s) updated."}})
    return response
