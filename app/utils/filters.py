# app/utils/filters.py

import pytz
from flask import session


def local_time(value, format="%b %d, %Y %I:%M %p"):
    if not value:
        return "—"

    # Get user's timezone from session, fallback to Asia/Manila
    tz_name = session.get("timezone", "Asia/Manila")

    try:
        user_tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        user_tz = pytz.timezone("Asia/Manila")

    # Ensure datetime is timezone-aware (assume UTC if naive)
    if value.tzinfo is None:
        value = pytz.utc.localize(value)

    local_dt = value.astimezone(user_tz)
    return local_dt.strftime(format)
