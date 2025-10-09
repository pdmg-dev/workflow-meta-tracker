# app/__init__.py
from flask import Flask

from scripts.seed_all import seed_all

from .blueprints import admin_bp, auth_bp, tracker_bp, voucher_bp
from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate
from .utils import filters


def create_app(config_class=None):
    app = Flask(__name__)
    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure extensions
    login_manager.login_view = "auth.login"

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tracker_bp)
    app.register_blueprint(voucher_bp)
    app.register_blueprint(admin_bp)

    # Register custom Jinja2 filters
    app.jinja_env.filters["local_time"] = filters.local_time
    app.jinja_env.filters["voucher_type"] = filters.voucher_type
    app.jinja_env.filters["voucher_status"] = filters.voucher_status
    app.jinja_env.filters["local_time_short"] = filters.local_time_short

    # Register event listeners
    from .utils import ref_number  # noqa: F401

    # Application Context
    with app.app_context():
        db.create_all()
        seed_all()

    return app
