# app/blueprints/auth/views.py
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.utils.navigation import get_dashboard_url

from . import auth_bp
from .forms import LoginForm
from .models import AuthIdentity


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())

    form = LoginForm()

    if form.validate_on_submit():
        identity = (
            db.session.query(AuthIdentity)
            .filter_by(username=form.username.data)
            .first()
        )
        if identity and identity.check_password(form.password.data):
            login_user(identity)
            flash("Logged in successfully.", "success")
            return redirect(get_dashboard_url())
        else:
            flash("Invalid username or password.", "error")
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
