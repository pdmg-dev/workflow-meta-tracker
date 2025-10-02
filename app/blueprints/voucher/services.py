# app/blueprints/voucher/services.py
from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models.voucher import Voucher, VoucherStatus, VoucherStatusHistory

local_timezone = ZoneInfo("Asia/Manila")


def create_voucher(form, current_user):
    status = VoucherStatus.query.filter_by(code="received").first()

    origin_id = form.origin_id.data if getattr(form, "origin_id", None) else None
    if not origin_id and getattr(form, "cleaned_origin", None):
        origin_id = form.cleaned_origin.id
    voucher = Voucher(
        voucher_type_id=form.voucher_type.data,
        fund=form.cleaned_fund,
        date_received=form.cleaned_date_received,
        payee=form.payee.data,
        origin_id=origin_id,
        address=form.address.data,
        amount=form.amount.data,
        particulars=form.particulars.data,
        status_id=status.id,
        encoded_by_id=current_user.id,
    )
    db.session.add(voucher)
    db.session.flush()

    history = VoucherStatusHistory(
        voucher_id=voucher.id,
        status_id=voucher.status_id,
        remarks=status.remarks,
        updated_by_id=voucher.encoded_by_id,
    )
    db.session.add(history)
    db.session.commit()

    return voucher


def parse_local_datetime(value):
    try:
        naive = datetime.strptime(value, "%m/%d/%Y %I:%M %p")
    except ValueError as error:
        raise ValueError("Invalid date format.") from error
    return naive.replace(tzinfo=local_timezone)


def get_current_local_datetime():
    return datetime.now(ZoneInfo("UTC")).astimezone(local_timezone).strftime("%m/%d/%Y %I:%M %p")


def to_local_datetime(date_time):
    if isinstance(date_time, str):
        parse_local_datetime(date_time)
    return date_time.astimezone(local_timezone).strftime("%m/%d/%Y %I:%M %p")


def get_todays_vouchers():
    current_date = datetime.now(local_timezone).date()
    start_time = datetime.combine(current_date, time.min).replace(tzinfo=local_timezone)
    end_time = datetime.combine(current_date, time.max).replace(tzinfo=local_timezone)
    return Voucher.query.filter(Voucher.encoded_at.between(start_time, end_time)).order_by(
        Voucher.encoded_at.desc(), Voucher.reference_number.desc()
    )
