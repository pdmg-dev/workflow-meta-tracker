# app/blueprints/voucher/services.py
from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models.voucher import Voucher, VoucherStatus, VoucherStatusHistory

local_timezone = ZoneInfo("Asia/Manila")


def create_voucher(form, current_user):
    status = VoucherStatus.query.filter_by(code="received").first()
    voucher = Voucher(
        voucher_type_id=form.voucher_type.data,
        origin_id=form.origin.data,
        date_received=form.date_received.data,
        payee=form.payee.data,
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


def get_current_local_datetime():
    return datetime.now(ZoneInfo("UTC")).astimezone(local_timezone).strftime("%m/%d/%Y %I:%M %p")


def to_local_datetime(datetime_data):
    return datetime_data.astimezone(local_timezone).strftime("%m/%d/%Y %I:%M %p")


def get_todays_vouchers():
    current_date = datetime.now(local_timezone).date()
    start_time = datetime.combine(current_date, time.min).replace(tzinfo=local_timezone)
    end_time = datetime.combine(current_date, time.max).replace(tzinfo=local_timezone)
    return Voucher.query.filter(Voucher.date_received.between(start_time, end_time)).order_by(
        Voucher.date_received, Voucher.reference_number.desc()
    )
