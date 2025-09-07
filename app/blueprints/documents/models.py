# app/blueprints/documents/models.py
from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"
    # __table_args__ = (db.UniqueConstraint("document_type_id",
    # "reference_number", name="uq_doc_type_ref"),)

    id = db.Column(db.Integer, primary_key=True)
    # reference_number = db.Column(db.String(50), unique=True, nullable=False)
    document_number = db.Column(db.String(50), unique=True, nullable=True)
    payee = db.Column(db.String(120), nullable=False)
    origin = db.Column(db.String(120), nullable=False)
    particulars = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Numeric(50, 2), nullable=True)
    date_received = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    document_type_id = db.Column(
        db.Integer, db.ForeignKey("document_types.id")
    )
    # status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    document_type = db.relationship(
        "DocumentType", backref="documents", lazy="joined"
    )
    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        backref="created_documents",
        lazy="joined",
    )
    changer = db.relationship(
        "User",
        foreign_keys=[changed_by],
        backref="changed_documents",
        lazy="joined",
    )
    # status = db.relationship("Status", backref="documents", lazy="joined")
    # status_history = db.relationship("StatusHistory", backref="document")


class DocumentType(db.Model):
    __tablename__ = "document_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
