import random
from datetime import datetime, timedelta, timezone

from app.blueprints.voucher.models import VoucherType
from app.extensions import db


def get_random_utc_datetime(days_range: int = 15):
    now = datetime.now(timezone.utc)
    offset = timedelta(days=random.uniform(-days_range, days_range))
    return now + offset


def get_random_doc_number():
    doc_types = db.session.query(VoucherType).all()
    codes = [doc.code for doc in doc_types]
    year = datetime.today().year
    return f"{random.choice(codes)}-{year}-{random.randint(100000, 999999)}"
