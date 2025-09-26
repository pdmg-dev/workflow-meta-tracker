# app/blueprints/vouchers/views.py

from datetime import datetime

import pytz
from flask import current_app, json, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.user import Role
from app.models.voucher import Voucher, VoucherStatus, VoucherStatusHistory, VoucherStatusTransition
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
            # Clean the form data and fetch default values
            payee = form.payee.data.strip()
            date_received = pytz.timezone("Asia/Manila").localize(form.date_received.data).astimezone(pytz.UTC)
            initial_status = db.session.query(VoucherStatus).filter_by(code="received").first()
            # Create and save a voucher
            new_voucher = Voucher(
                payee=payee,
                amount=form.amount.data,
                particulars=form.particulars.data,
                origin=form.origin.data,
                date_received=date_received,
                voucher_type_id=form.voucher_type.data,
                status_id=initial_status.id,
                encoded_by_id=current_user.id,
            )
            db.session.add(new_voucher)
            db.session.commit()
            # Create and save initial voucher status history
            history = VoucherStatusHistory(
                remarks=initial_status.remarks,
                voucher_id=new_voucher.id,
                status_id=new_voucher.status_id,
                updated_by_id=new_voucher.encoded_by_id,
            )
            db.session.add(history)
            db.session.commit()

            # HTMX partial refresh: return a new blank form + trigger toast
            if request.headers.get("HX-Request"):
                fresh_form = VoucherForm(formdata=None)  # Make sure the form has no data inputs
                response = make_response(render_template("voucher/form.html", form=fresh_form))
                # HX-Trigger with JSON payload so JS can read e.detail.voucherSaved.message
                response.headers["HX-Trigger"] = json.dumps(
                    {
                        "voucherSaved": {
                            "message": f"Voucher {new_voucher.reference_number} saved.",
                            "id": new_voucher.id,
                        }
                    }
                )
                return response
            return redirect(url_for("voucher.new_voucher"))

        if request.headers.get("HX-Request"):
            current_app.logger.warning("Form errors: %s", form.errors)

            return make_response(render_template("voucher/form.html", form=form), 200)
        return render_template("new_voucher.html", form=form)
    # Request method: GET -> Show empty form
    tz = pytz.UTC
    today_utc = datetime.now(tz).date()
    start = datetime.combine(today_utc, datetime.min.time()).replace(tzinfo=tz)
    end = datetime.combine(today_utc, datetime.max.time()).replace(tzinfo=tz)
    vouchers = Voucher.query.filter(Voucher.date_received.between(start, end)).order_by(
        Voucher.date_received.desc(), Voucher.reference_number.desc()
    )
    # Get the most recent voucher (if any)
    recent_voucher = vouchers.first_or_404() if vouchers.count() > 0 else None
    return render_template(
        "new_voucher.html",
        form=form,
        vouchers=vouchers,
        recent_voucher_id=recent_voucher.id if recent_voucher else None,
    )


# app/blueprints/voucher/views.py
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


@voucher_bp.route("/voucher/<int:voucher_id>")
@login_required
def particulars(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    if not voucher:
        return "", 204
    return render_template("voucher/_particulars.html", voucher=voucher)


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
