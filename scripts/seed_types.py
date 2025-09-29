from app.extensions import db
from app.models.voucher import VoucherType


def seed_voucher_types():
    default_voucher_types = [
        {"name": "Payroll", "code": "PAY"},
        {"name": "Salary", "code": "SAL"},
        {"name": "Travel", "code": "TEV"},
        {"name": "Gasoline", "code": "GAS"},
        {"name": "Telephone", "code": "TEL"},
        {"name": "Donation", "code": "DON"},
        {"name": "Projects", "code": "PRJ"},
        {"name": "Others", "code": "OTH"},
    ]

    for vt in default_voucher_types:
        existing = db.session.query(VoucherType).filter_by(code=vt["code"]).first()
        if not existing:
            voucher_type = VoucherType(name=vt["name"], code=vt["code"])
            db.session.add(voucher_type)

    db.session.commit()
    print("✅ Voucher types seeded successfully.")
