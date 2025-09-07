# app/utils/metadata.py
from datetime import date

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.blueprints.documents import models


@event.listens_for(models.Document, "before_insert")
def generate_reference_number(mapper, connection, target):
    print("Listener triggered for:", target)
    if target.reference_number:
        return

    session = Session(bind=connection)

    doc_type = (
        session.query(models.DocumentType)
        .filter_by(id=target.document_type_id)
        .first()
    )
    doc_type_code = (
        doc_type.code.upper() if doc_type and doc_type.code else "DOC"
    )

    year = date.today().year
    pattern = f"{doc_type_code}-{year}-%"

    last_doc = (
        session.query(models.Document)
        .filter(models.Document.reference_number.like(pattern))
        .order_by(models.Document.id.desc())
        .first()
    )

    new_seq = (
        int(last_doc.reference_number.split("-")[-1]) + 1
        if last_doc and last_doc.reference_number
        else 1
    )
    target.reference_number = f"{doc_type_code}-{year}-{new_seq:04d}"
