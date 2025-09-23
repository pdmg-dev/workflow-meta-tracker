from datetime import date

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.voucher import Voucher, VoucherType


@event.listens_for(Voucher, "before_insert")
def generate_reference_number(mapper, connection, target):
    if target.reference_number:
        return

    session = Session(bind=connection)

    # Get voucher type code
    voucher_type = session.query(VoucherType).filter_by(id=target.voucher_type_id).first()
    voucher_type_code = voucher_type.code.upper() if voucher_type and voucher_type.code else "DOC"

    year = date.today().year
    year_prefix = f"-{year}-"

    # Count vouchers of this type for the year
    type_count = session.query(Voucher).filter(Voucher.reference_number.like(f"{voucher_type_code}-{year}-%")).count()

    # Count all vouchers for the year
    overall_count = session.query(Voucher).filter(Voucher.reference_number.like(f"%{year_prefix}%")).count()

    # Increment both counts
    type_seq = type_count + 1
    overall_seq = overall_count + 1

    # Format reference number
    target.reference_number = f"{voucher_type_code}-{year}-{type_seq:04d}-{overall_seq:04d}"
