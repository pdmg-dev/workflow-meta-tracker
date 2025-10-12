from app.extensions import db
from app.models.user import User
from app.models.voucher import VoucherType


def seed_user_vouchers():
    voucher_types = db.session.query(VoucherType).all()
    user_map = {
        "tin": ["Projects", "Salary", "Others"],
        "cecil": ["Payroll"],
        "jade": ["Travel", "Gasoline"],
        "mau": ["Projects", "Telephone", "Donation"],
        "ivy": [voucher_type.name for voucher_type in voucher_types],
    }

    for username, voucher_names in user_map.items():
        user = User.query.filter_by(username=username).first()
        if not user:
            continue
        voucher_types = VoucherType.query.filter(VoucherType.name.in_(voucher_names)).all()
        user.voucher_types = voucher_types

    db.session.commit()
    print("✅ Voucher types assigned to users.")
