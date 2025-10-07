# app/blueprints/vouchers/models.py
from datetime import datetime, timezone

from sqlalchemy import func

from app.extensions import db

from .user import role_voucher_types, status_transition_roles, user_voucher_types


class Voucher(db.Model):
    __tablename__ = "vouchers"
    __table_args__ = (db.Index("ix_reference_number", "reference_number"),)

    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(50), unique=True, nullable=False)
    payee = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    particulars = db.Column(db.Text, nullable=False)

    date_received = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    voucher_type_id = db.Column(db.Integer, db.ForeignKey("voucher_types.id"), nullable=False)
    origin_id = db.Column(db.Integer, db.ForeignKey("voucher_origins.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("voucher_statuses.id"), nullable=False)

    encoded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    encoded_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    edited_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    voucher_type = db.relationship("VoucherType", back_populates="vouchers", lazy="joined")
    origin = db.relationship("VoucherOrigin", back_populates="vouchers", lazy="joined")
    status = db.relationship("VoucherStatus", back_populates="vouchers", lazy="joined")

    encoder = db.relationship("User", foreign_keys=[encoded_by_id], back_populates="encoded_vouchers")
    editor = db.relationship("User", foreign_keys=[edited_by_id], back_populates="edited_vouchers")
    updater = db.relationship("User", foreign_keys=[updated_by_id], back_populates="updated_vouchers")

    history = db.relationship(
        "VoucherStatusHistory", back_populates="voucher", cascade="all, delete-orphan", lazy="dynamic"
    )


class VoucherType(db.Model):
    __tablename__ = "voucher_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

    vouchers = db.relationship("Voucher", back_populates="voucher_type")
    roles = db.relationship("Role", secondary=role_voucher_types, back_populates="voucher_types")
    users = db.relationship("User", secondary=user_voucher_types, back_populates="voucher_types")


class VoucherOrigin(db.Model):
    __tablename__ = "voucher_origins"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    keyword = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

    vouchers = db.relationship("Voucher", back_populates="origin")


class VoucherStatus(db.Model):
    __tablename__ = "voucher_statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    remarks = db.Column(db.String(255))

    vouchers = db.relationship("Voucher", back_populates="status")
    histories = db.relationship("VoucherStatusHistory", back_populates="status")


class VoucherStatusTransition(db.Model):
    __tablename__ = "voucher_status_transitions"

    id = db.Column(db.Integer, primary_key=True)
    from_status_id = db.Column(db.Integer, db.ForeignKey("voucher_statuses.id"), nullable=False)
    to_status_id = db.Column(db.Integer, db.ForeignKey("voucher_statuses.id"), nullable=False)

    from_status = db.relationship("VoucherStatus", foreign_keys=[from_status_id])
    to_status = db.relationship("VoucherStatus", foreign_keys=[to_status_id])

    allowed_roles = db.relationship("Role", secondary=status_transition_roles, back_populates="allowed_transitions")


class VoucherStatusHistory(db.Model):
    __tablename__ = "voucher_status_history"

    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String(255))
    voucher_id = db.Column(db.Integer, db.ForeignKey("vouchers.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("voucher_statuses.id"), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    voucher = db.relationship("Voucher", back_populates="history")
    status = db.relationship("VoucherStatus", back_populates="histories")
    updated_by_user = db.relationship(
        "User", foreign_keys=[updated_by_id], back_populates="status_updates", lazy="joined"
    )
