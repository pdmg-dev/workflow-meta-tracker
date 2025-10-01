# app/blueprints/vouchers/views.py

from datetime import datetime

import pytz
from flask import flash, json, jsonify, make_response, render_template, request
from flask_login import current_user, login_required

from app.blueprints.voucher.services import (
    create_voucher,
    get_todays_vouchers,
)
from app.extensions import db
from app.models.user import Role
from app.models.voucher import Voucher, VoucherOrigin, VoucherStatusHistory, VoucherStatusTransition
from app.utils.access_control import require_roles

from . import voucher_bp
from .forms import VoucherForm


@voucher_bp.route("/voucher/new", methods=["GET", "POST"])
@login_required
@require_roles("admin", "encoder")
def new_voucher():
    form = VoucherForm()
    if request.method == "POST":
        if form.validate_on_submit():
            new_voucher = create_voucher(form, current_user)
            flash("Voucher saved successfully!", "success")
            new_form = VoucherForm(formdata=None)  # Load a new form
            # Reload the fragments (cards) in the page
            return render_template(
                "voucher/_new_voucher_fragments.html",
                form=new_form,
                vouchers=get_todays_vouchers(),
                new_voucher=new_voucher,
            )
        else:
            # If form validation failed, retain input data
            return render_template(
                "voucher/_form.html",
                form=form,
            )

    # Load a new form, if cancel button is clicked
    if request.args.get("clear_form") == "true":
        form = VoucherForm(formdata=None)
        return render_template("voucher/_form.html", form=form)

    # GET request contexts
    return render_template(
        "new_voucher.html", form=form, vouchers=get_todays_vouchers(), voucher=get_todays_vouchers().first()
    )


# app/blueprints/vouchers/routes.py
@voucher_bp.route("/voucher/origin-suggest")
@login_required
def origin_suggest():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = (
        db.session.query(VoucherOrigin.name)
        .filter(VoucherOrigin.name.ilike(f"%{q}%"))
        .order_by(VoucherOrigin.name)
        .limit(10)
        .all()
    )
    return jsonify([r.name for r in results])


@voucher_bp.route("/vouchers/today", methods=["GET"])
@login_required
def todays_vouchers():
    tz = pytz.UTC
    today_utc = datetime.now(tz).date()
    start = datetime.combine(today_utc, datetime.min.time()).replace(tzinfo=tz)
    end = datetime.combine(today_utc, datetime.max.time()).replace(tzinfo=tz)

    vouchers = Voucher.query.filter(Voucher.date_received.between(start, end)).order_by(
        Voucher.date_received.desc(), Voucher.reference_number.desc()
    )
    return render_template("voucher/_today.html", vouchers=vouchers)


@voucher_bp.route("/voucher/preview/<int:voucher_id>")
@login_required
def details_preview(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    if not voucher:
        return "", 204
    history = voucher.history.order_by(VoucherStatusHistory.updated_at.desc()).all()
    return render_template("voucher/_preview.html", voucher=voucher, history=history)


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
