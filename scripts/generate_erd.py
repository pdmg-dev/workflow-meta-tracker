# scripts/generate_erd.py
from eralchemy import render_er

from app import create_app
from app.blueprints.users import models as user_models  # noqa: F401
from app.blueprints.voucher import models as voucher_models  # noqa: F401
from app.extensions import db


# Custom config just for ERD generation
class ERDConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Pass the config class into create_app
app = create_app(config_class=ERDConfig)

with app.app_context():
    render_er(db.Model, "app_erd.png")
