# app/__init__.py
from flask import Flask
from .extensions import db, bcrypt, migrate, login_manager
from .config import get_config


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app
