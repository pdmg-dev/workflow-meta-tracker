from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.voucher import Voucher  # Adjust import paths as needed


@event.listens_for(Voucher, "before_insert")
def generate_reference_number(mapper, connection, target):
    if target.reference_number:
        return

    session = Session(bind=connection)

    # Use actual date received if available, else fallback to now
    received_date = target.date_received or datetime.now()
    year = received_date.year
    month = received_date.month

    # Count all vouchers for the same year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    overall_count = (
        session.query(Voucher)
        .filter(Voucher.date_received >= start_of_year, Voucher.date_received < end_of_year)
        .count()
    )
    overall_seq = overall_count + 1

    # Format reference number
    target.reference_number = f"#{year % 100:02d}{month:02d}{overall_seq:04d}"
