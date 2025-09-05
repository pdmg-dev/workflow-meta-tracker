# app/blueprints/auth/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.users import models
from app.extensions import db
from app.utils.routing import redirect_to_dashboard

from . import auth_bp
from .forms import LoginForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(models.User).filter_by(username=form.username.data)).scalar_one_or_none()
        if not user:
            flash("Username not found. Please try again.")
        elif not user.check_password(form.password.data):
            flash("Incorrect password. Please try again.")
        else:
            login_user(user)
            flash("Logged in successfully.")
            return redirect_to_dashboard(user)
    return render_template("auth/login.html", form=form)


@auth_bp.route("logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("auth.login"))
