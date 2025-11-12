# app/blueprints/auth/routes.py
from datetime import datetime, timedelta, timezone

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db, socketio
from app.models.user import User

from . import auth_bp
from .forms import LoginForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.is_active:
        flash("You are already logged in.", "info")
        return redirect(url_for("tracker.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data, duration=timedelta(days=7))

            # Update presence
            user.last_login = datetime.now(timezone.utc)
            user.is_online = True
            db.session.commit()

            # Emit presence event
            socketio.emit("user_online", {"user_id": user.id, "username": user.username}, namespace="/presence")

            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("tracker.dashboard"))

        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    user = current_user

    user.last_logout = datetime.now(timezone.utc)
    user.is_online = False
    db.session.commit()

    # Emit presence event
    socketio.emit("user_offline", {"user_id": user.id, "username": user.username}, namespace="/presence")

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
