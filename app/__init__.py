# app/__init__.py
from flask import Flask

from .blueprints import auth_bp
from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    return app
