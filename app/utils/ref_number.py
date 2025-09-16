# app/utils/ref_number.py
from datetime import date

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.voucher import Voucher, VoucherType


@event.listens_for(Voucher, "before_insert")
def generate_reference_number(mapper, connection, target):
    if target.reference_number:  # Check if reference number is already set
        return

    session = Session(bind=connection)
    # Retrieve the voucher_type code
    voucher_type = session.query(VoucherType).filter_by(id=target.voucher_type_id).first()
    voucher_type_code = voucher_type.code.upper() if voucher_type and voucher_type.code else "DOC"

    # Contstruct the pattern
    year = date.today().year
    pattern = f"{voucher_type_code}-{year}-%"

    # Fetch the latest voucher
    last_voucher = (
        session.query(Voucher).filter(Voucher.reference_number.like(pattern)).order_by(Voucher.id.desc()).first()
    )

    # Set the next number sequence
    new_seq = (
        int(last_voucher.reference_number.split("-")[-1]) + 1 if last_voucher and last_voucher.reference_number else 1
    )
    # Assigne the generated reference number
    target.reference_number = f"{voucher_type_code}-{year}-{new_seq:04d}"
