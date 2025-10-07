# app/utils/filters.py

import pytz
from flask import session

from app.models.voucher import VoucherStatus, VoucherType

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


def voucher_type(vouchers, code):
    return vouchers.join(VoucherType).filter(VoucherType.code == code).count()


def voucher_status(vouchers, code):
    return vouchers.join(VoucherStatus).filter(VoucherStatus.code == code).count()
