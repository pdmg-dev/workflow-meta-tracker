from app.extensions import db
from app.models.voucher import VoucherOrigin


def seed_voucher_origin():
    default_voucher_origins = [
        {"name": "Office of the Mayor", "code": "1011"},
        {"name": "Office of the Vice Mayor", "code": "1016"},
        {"name": "Sangguniang Bayan (SB)", "code": "1021"},
        {"name": "Municipal Disaster Risk Reduction Management Office (MDRRM0)", "code": "9991"},
        {"name": "Municipal Disaster Risk Reduction Management Office (MDRRMF)", "code": "9991"},
        {"name": "Municipal Planning and Development Coordinator (MPDC)", "code": "1041"},
        {"name": "Municipal Social Welfare and Development Office (MSWDO)", "code": "7611"},
        {"name": "Municipal Agriculture Office (MAO)", "code": "8711"},
        {"name": "Municipal Health Office (MHO)", "code": "4411"},
        {"name": "Municipal Engineer's Office (MEO)", "code": "8751"},
        {"name": "Municipal Treasurer's Office (MTO)", "code": "1091"},
        {"name": "Office of the Municipal Assessor", "code": "1101"},
        {"name": "Office of the Municipal Accountant (OMA)", "code": "1081"},
        {"name": "Municipal Civil Registrar's Office (MCRO)", "code": "1051"},
        {"name": "Municipal Budget Office (MBO)", "code": "1071"},
        {"name": "Municipal Environment and Natural Resources Office (MENRO)", "code": "8731"},
        {"name": "Municipal Tourism Office", "code": "Tourism"},
        {"name": "Human Resource and Management Office", "code": "Human Resource"},
    ]

    for vo in default_voucher_origins:
        existing = db.session.query(VoucherOrigin).filter_by(code=vo["code"]).first()
        if not existing:
            voucher_origin = VoucherOrigin(name=vo["name"], code=vo["code"])
            db.session.add(voucher_origin)

    db.session.commit()
    print("✅ Voucher origins seeded successfully.")
