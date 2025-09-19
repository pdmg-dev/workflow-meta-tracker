# app/blueprints/vouchers/views.py

import pytz
from flask import current_app, json, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.voucher import Voucher, VoucherStatus, VoucherStatusHistory
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
                    {"voucherSaved": {"message": f"Voucher {new_voucher.reference_number} saved."}}
                )
                return response
            return redirect(url_for("voucher.new_voucher"))

        if request.headers.get("HX-Request"):
            current_app.logger.warning("Form errors: %s", form.errors)

            return make_response(render_template("voucher/form.html", form=form), 200)
        return render_template("new_voucher.html", form=form)
    # Request method: GET -> Show empty form
    return render_template("new_voucher.html", form=form)


@voucher_bp.route("/voucher/<int:voucher_id>")
@login_required
def particulars(voucher_id):
    voucher = db.session.get(Voucher, voucher_id)
    if not voucher:
        return "", 404
    return render_template("voucher/_particulars.html", voucher=voucher)


"""
@voucher_bp.route("/all", methods=["GET", "POST"])
@login_required
def view_all_documents():
    documents = db.session.query(Voucher).order_by(Voucher.date_received.desc()).all()

    # Show the current document status in the form
    form = {}
    for doc in documents:
        status_form = StatusUpdateForm()
        status_form.status.data = doc.status_id  # Set current status
        form[doc.id] = status_form

    return render_template("documents/list.html", documents=documents, form=form)


@voucher_bp.route("<int:doc_id>", methods=["GET"])
@login_required
def view_document(doc_id):
    document = db.session.query(Voucher).get(doc_id)
    return render_template("documents/detail.html", document=document)


@voucher_bp.route("/<int:doc_id>/update-status", methods=["GET", "POST"])
@login_required
def update_status(doc_id):
    document = db.session.query(Voucher).get(doc_id)
    form = StatusUpdateForm(obj=document)

    if form.validate_on_submit():
        new_status_id = form.status.data
        note = form.note.data

        document.status_id = new_status_id
        status = db.session.query(Status).get(new_status_id)

        final_note = note.strip() if note and note.strip() else status.default_note

        history = StatusHistory(
            document_id=doc_id,
            status_id=new_status_id,
            changed_by=current_user.id,
            note=final_note,
        )
        db.session.add(history)
        db.session.commit()

        flash("Status updated and history logged.", "success")
        return redirect(url_for("documents.view_all_documents"))

    return render_template("documents/update_status.html", form=form, document=document)
"""
