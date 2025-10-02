from app.extensions import db
from app.models.voucher import VoucherFund


def seed_funds():
    dafault_voucher_funds = [
        {"name": "General", "code": "100"},
        {"name": "Special", "code": "200"},
        {"name": "Trust", "code": "300"},
    ]

    for fund_data in dafault_voucher_funds:
        existing = db.session.query(VoucherFund).filter_by(code=fund_data["code"]).first()
        if not existing:
            fund = VoucherFund(name=fund_data["name"], code=fund_data["code"])
            db.session.add(fund)

    db.session.commit()
    print("✅ Funds seeded successfully.")
