# app/blueprints/users/models.py

from flask_login import UserMixin

from app.extensions import bcrypt, db

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    roles = db.relationship("Role", secondary=user_roles, back_populates="users")

    encoded_vouchers = db.relationship("Voucher", foreign_keys="Voucher.encoded_by_id", back_populates="encoder")

    updated_vouchers = db.relationship("Voucher", foreign_keys="Voucher.updated_by_id", back_populates="updater")

    status_updates = db.relationship(
        "VoucherStatusHistory",
        foreign_keys="VoucherStatusHistory.updated_by_id",
        back_populates="updated_by_user",
        lazy="dynamic",
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


role_voucher_types = db.Table(
    "role_voucher_types",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("voucher_type_id", db.Integer, db.ForeignKey("voucher_types.id"), primary_key=True),
)

status_transition_roles = db.Table(
    "status_transition_roles",
    db.Column("transition_id", db.Integer, db.ForeignKey("voucher_status_transitions.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(25), unique=True, nullable=False)

    users = db.relationship("User", secondary=user_roles, back_populates="roles")

    voucher_types = db.relationship("VoucherType", secondary=role_voucher_types, back_populates="roles")

    allowed_transitions = db.relationship(
        "VoucherStatusTransition", secondary=status_transition_roles, back_populates="allowed_roles"
    )
