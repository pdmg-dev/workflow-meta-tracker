from app.extensions import db
from app.models.user import User
from app.models.voucher import VoucherType


def seed_user_vouchers():
    voucher_types = db.session.query(VoucherType).all()
    user_map = {
        "Tin": ["Projects", "Salary", "Others"],
        "Cecil": ["Payroll"],
        "Jade": ["Travel", "Gasoline"],
        "Mau": ["Projects", "Telephone", "Donation"],
        "Ivy": voucher_types,
    }

    for full_name, voucher_names in user_map.items():
        user = User.query.filter_by(full_name=full_name).first()
        if not user:
            continue
        voucher_types = VoucherType.query.filter(VoucherType.name.in_(voucher_names)).all()
        user.voucher_types = voucher_types

    db.session.commit()
    print("✅ Voucher types assigned to users.")
