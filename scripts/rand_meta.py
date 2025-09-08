import random
from datetime import datetime, timedelta, timezone

from app.blueprints.documents.models import DocumentType
from app.extensions import db


def get_random_utc_datetime(days_range: int = 15):
    now = datetime.now(timezone.utc)
    offset = timedelta(days=random.uniform(-days_range, days_range))
    return now + offset


def get_random_doc_number():
    doc_types = db.session.query(DocumentType).all()
    codes = [doc.code for doc in doc_types]
    year = datetime.today().year
    return f"{random.choice(codes)}-{year}-{random.randint(100000, 999999)}"
