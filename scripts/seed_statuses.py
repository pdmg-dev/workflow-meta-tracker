from app.extensions import db
from app.models.voucher import VoucherStatus


def seed_statuses():
    dafault_statuses = [
        {"name": "Received", "code": "received", "remarks": "For Review"},
        {"name": "Checked", "code": "checked", "remarks": "For Processing"},
        {"name": "Sorted", "code": "sorted", "remarks": "For Approval"},
        {"name": "Approved", "code": "approved", "remarks": "For Released"},
        {"name": "Returned", "code": "returned", "remarks": ""},
    ]

    for status_data in dafault_statuses:
        existing = db.session.query(VoucherStatus).filter_by(code=status_data["code"]).first()
        if not existing:
            status = VoucherStatus(name=status_data["name"], code=status_data["code"], remarks=status_data["remarks"])
            db.session.add(status)

    db.session.commit()
    print("✅ Statues seeded successfully.")
