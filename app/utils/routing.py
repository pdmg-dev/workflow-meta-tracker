# app/utils/routing.py
from flask import flash, redirect, url_for


def redirect_to_dashboard(identity):
    match identity.role:
        case "admin":
            return redirect(url_for("admin.dashboard"))
        case "staff":
            return redirect(url_for("staff.dashboard"))
        case _:
            flash("Unknown role.")
            return redirect(url_for("auth.login"))
