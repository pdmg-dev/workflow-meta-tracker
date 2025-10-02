from app.extensions import db
from app.models.voucher import VoucherOrigin


def seed_voucher_origin():
    default_voucher_origins = [
        {"name": "Office of the Mayor", "code": "1011", "keyword": "Mayor"},
        {"name": "Office of the Vice Mayor", "code": "1016", "keyword": "Vice Mayor"},
        {"name": "Sangguniang Bayan (SB)", "code": "1021", "keyword": "SB"},
        {"name": "Municipal Disaster Risk Reduction Management Office (MDRRMO)", "code": "9991", "keyword": "MDRRMO"},
        {"name": "Municipal Disaster Risk Reduction Management Office (MDRRMF)", "code": "9992", "keyword": "MDRRMF"},
        {"name": "Municipal Planning and Development Coordinator (MPDC)", "code": "1041", "keyword": "Planning"},
        {
            "name": "Municipal Social Welfare and Development Office (MSWDO)",
            "code": "7611",
            "keyword": "Social Welfare",
        },
        {"name": "Municipal Agriculture Office (MAO)", "code": "8711", "keyword": "Agriculture"},
        {"name": "Municipal Health Office (MHO)", "code": "4411", "keyword": "Health"},
        {"name": "Municipal Engineer's Office (MEO)", "code": "8751", "keyword": "Engineering"},
        {"name": "Municipal Treasurer's Office (MTO)", "code": "1091", "keyword": "Treasury"},
        {"name": "Office of the Municipal Assessor", "code": "1101", "keyword": "Assessor"},
        {"name": "Office of the Municipal Accountant (OMA)", "code": "1081", "keyword": "Accounting"},
        {"name": "Municipal Civil Registrar's Office (MCRO)", "code": "1051", "keyword": "Registrar"},
        {"name": "Municipal Budget Office (MBO)", "code": "1071", "keyword": "Budget"},
        {"name": "Municipal Environment and Natural Resources Office (MENRO)", "code": "8731", "keyword": "MENRO"},
        {"name": "Municipal Tourism Office", "code": "Tourism", "keyword": "Tourism"},
        {"name": "Human Resource and Management Office", "code": "Human Resource", "keyword": "HR"},
    ]

    for vo in default_voucher_origins:
        existing = db.session.query(VoucherOrigin).filter_by(code=vo["code"]).first()
        if not existing:
            voucher_origin = VoucherOrigin(name=vo["name"], code=vo["code"], keyword=vo["keyword"])
            db.session.add(voucher_origin)

    db.session.commit()
    print("✅ Voucher origins seeded successfully.")
