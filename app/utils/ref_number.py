from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.voucher import Voucher, VoucherType  # Adjust import paths as needed


@event.listens_for(Voucher, "before_insert")
def generate_reference_number(mapper, connection, target):
    if target.reference_number:
        return

    session = Session(bind=connection)

    # Get voucher type code
    voucher_type = session.query(VoucherType).filter_by(id=target.voucher_type_id).first()
    voucher_type_code = voucher_type.code.upper() if voucher_type and voucher_type.code else "DOC"

    # Use actual date received if available, else fallback to now
    received_date = target.date_received or datetime.now()
    year = received_date.year
    month = received_date.month

    # Calculate start and end of month
    start_of_month = datetime(year, month, 1)
    if month == 12:
        end_of_month = datetime(year + 1, 1, 1)
    else:
        end_of_month = datetime(year, month + 1, 1)

    # Count vouchers of this type for the same month
    type_count = (
        session.query(Voucher)
        .filter(
            Voucher.voucher_type_id == target.voucher_type_id,
            Voucher.date_received >= start_of_month,
            Voucher.date_received < end_of_month,
        )
        .count()
    )

    # Count all vouchers for the same year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    overall_count = (
        session.query(Voucher)
        .filter(Voucher.date_received >= start_of_year, Voucher.date_received < end_of_year)
        .count()
    )

    # Increment both counts
    type_seq = type_count + 1
    overall_seq = overall_count + 1

    # Format reference number
    target.reference_number = f"{voucher_type_code}-{type_seq:03d}-{year}{month:02d}-{overall_seq:04d}"
