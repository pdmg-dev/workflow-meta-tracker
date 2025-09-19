# app/blueprints/auth/views.py
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models.user import User

from . import auth_bp
from .forms import LoginForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("tracker.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("tracker.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
