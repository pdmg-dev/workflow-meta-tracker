# app/__init__.py
from flask import Flask

from scripts.seed import seed_data

from .blueprints import admin_bp, auth_bp, document_bp, main_bp, staff_bp
from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate
from .utils.navigation import get_dashboard_url


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure extensions
    login_manager.login_view = "auth.login"

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(document_bp)

    # Global functions
    app.jinja_env.globals["url_for_dashboard"] = get_dashboard_url

    # Register event listeners
    from .utils import metadata  # noqa: F401

    # Application Context
    with app.app_context():
        db.create_all()
        seed_data()

    return app
