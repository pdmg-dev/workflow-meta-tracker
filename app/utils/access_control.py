from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user


def require_roles(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You need to log in to access this feature.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            user_role_codes = {role.code for role in current_user.roles}
            if not any(role in user_role_codes for role in allowed_roles):
                flash("You don't have permission to perform this action.", "danger")
                return redirect(request.referrer or url_for("tracker.dashboard"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
