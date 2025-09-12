# app/blueprints/statuses/models.py
from datetime import datetime, timezone

from app.extensions import db


class Status(db.Model):
    __tablename__ = "statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    default_note = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)


class StatusHistory(db.Model):
    __tablename__ = "status_histories"

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)

    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"))
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    changed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    status = db.relationship("Status", lazy="joined")
    changer = db.relationship("User", lazy="joined")

    @property
    def resolved_note(self):
        return self.note or self.status.default_note or "—"
