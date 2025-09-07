# app/utils/routing.py
from flask import url_for
from flask_login import current_user


def get_dashboard_url():
    if not current_user.is_authenticated:
        return url_for("auth.login")

    match current_user.role:
        case "admin":
            return url_for("admin.dashboard")
        case "staff":
            return url_for("staff.dashboard")
        case _:
            return url_for("auth.login")
