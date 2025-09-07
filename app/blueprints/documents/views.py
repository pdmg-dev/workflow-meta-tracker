# app/blueprints/documents/views.py
from flask import flash, redirect, render_template, url_for
from flask_login import login_required

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
            date_received=form.date_received.data,
        )

        db.session.add(new_document)
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
    return render_template("documents/list.html", documents=documents)
