# app/utils/filters.py

import pytz
from flask import session

format = "%m-%d-%y %I:%M %p"


def local_time(value, format=format):
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


short_format = "%m-%d %I:%M %p"


def local_time_short(value, format=short_format):
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


def name_shortener(fullname):
    initials = [char for char in fullname[::-1] if char.isupper()]
    fn = fullname.split(" ")[0]
    short_name = f"{fn} {initials[0]}."
    return short_name
