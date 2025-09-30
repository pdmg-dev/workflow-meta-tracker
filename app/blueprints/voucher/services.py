# app/blueprints/voucher/services.py
from app.extensions import db
from app.models.voucher import Voucher, VoucherStatus, VoucherStatusHistory


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
