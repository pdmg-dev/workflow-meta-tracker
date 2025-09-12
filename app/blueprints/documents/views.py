# app/blueprints/documents/views.py
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.blueprints.statuses.forms import StatusUpdateForm
from app.blueprints.statuses.models import Status, StatusHistory
from app.extensions import db

from . import document_bp
from .forms import DocumentForm
from .models import Document


@document_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_document():
    form = DocumentForm()

    if form.validate_on_submit():
        new_document = Document(
            document_type_id=form.document_type.data,
            document_number=form.document_number.data,
            payee=form.payee.data,
            origin=form.origin.data,
            particulars=form.particulars.data,
            amount=form.amount.data,
            status_id=form.status.data,
            date_received=form.date_received.data,
            created_by=current_user.id,
        )

        # First, add and commit the document to get its ID
        db.session.add(new_document)
        db.session.commit()

        # Automatically log status history as "Received"
        status = db.session.query(Status).get(new_document.status_id)
        history = StatusHistory(
            document_id=new_document.id,
            status_id=new_document.status_id,
            changed_by=current_user.id,
            note=status.default_note,
        )
        db.session.add(history)
        db.session.commit()

        flash("Document added successfully.", "success")
        return redirect(url_for("documents.create_document"))

    return render_template("documents/form.html", form=form)


@document_bp.route("/all", methods=["GET", "POST"])
@login_required
def view_all_documents():
    documents = (
        db.session.query(Document)
        .order_by(Document.date_received.desc())
        .all()
    )

    # Show the current document status in the form
    form = {}
    for doc in documents:
        status_form = StatusUpdateForm()
        status_form.status.data = doc.status_id  # Set current status
        form[doc.id] = status_form

    return render_template(
        "documents/list.html", documents=documents, form=form
    )


@document_bp.route("<int:doc_id>", methods=["GET"])
@login_required
def view_document(doc_id):
    document = db.session.query(Document).get(doc_id)
    return render_template("documents/detail.html", document=document)


STATUS_NOTES = {
    "Received": "For Review",
    "Checked & Verified": "For Processing",
    "Sorted & Prepared": "For Approval",
    "Approved & Signed": "For Released",
    "Returned": "",
}


@document_bp.route("/<int:doc_id>/update-status", methods=["GET", "POST"])
@login_required
def update_status(doc_id):
    document = db.session.query(Document).get(doc_id)
    form = StatusUpdateForm(obj=document)

    if form.validate_on_submit():
        new_status_id = form.status.data
        note = form.note.data

        document.status_id = new_status_id
        status = db.session.query(Status).get(new_status_id)

        final_note = (
            note.strip() if note and note.strip() else status.default_note
        )

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

    return render_template(
        "documents/update_status.html", form=form, document=document
    )
