# app/blueprints/auth/models.py
from flask_login import UserMixin

from app.extensions import bcrypt, db


class AuthIdentity(UserMixin, db.Model):
    __tablename__ = "auth_identities"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode(
            "utf-8"
        )

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    user = db.relationship("User", backref="auth_identity", lazy="joined")

    @property
    def role(self):
        return self.user.role if self.user else None
