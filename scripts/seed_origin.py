from app.extensions import db
from app.models.voucher import VoucherOrigin


def seed_voucher_origin():
    default_voucher_origins = [
        {"name": "Office of the Mayor", "code": "Mayor"},
        {"name": "Office of the Vice Mayor", "code": "Vice"},
        {"name": "Sangguniang Bayan (SB)", "code": "SB"},
        {"name": "Municipal Disaster Risk Reduction Management Office (MDRRMO)", "code": "MDRRMO"},
        {"name": "Municipal Planning and Development Coordinator (MPDC)", "code": "MPDC"},
        {"name": "Human Resource and Management Office (HRMO)", "code": "HRMO"},
        {"name": "Municipal Social Welfare and Development Office (MSWDO)", "code": "MSWDO"},
        {"name": "Municipal Agriculture Office (MAO)", "code": "MAO"},
        {"name": "Municipal Health Office (MHO)", "code": "MHO"},
        {"name": "Municipal Engineer's Office (MEO)", "code": "MEO"},
        {"name": "Municipal Treasurer's Office (MTO)", "code": "MTO"},
        {"name": "Office of the Municipal Assessor", "code": "Assessor"},
        {"name": "Office of the Municipal Accountant (OMA)", "code": "OMA"},
        {"name": "Municipal Civil Registrar's Office (MCRO)", "code": "MCRO"},
        {"name": "Municipal Tourism Office", "code": "Tourism"},
        {"name": "Municipal Budget Office (MBO)", "code": "MBO"},
        {"name": "Municipal Environment and Natural Resources Office (MENRO)", "code": "MENRO"},
    ]

    for vo in default_voucher_origins:
        existing = db.session.query(VoucherOrigin).filter_by(code=vo["code"]).first()
        if not existing:
            voucher_origin = VoucherOrigin(name=vo["name"], code=vo["code"])
            db.session.add(voucher_origin)

    db.session.commit()
    print("✅ Voucher origins seeded successfully.")
