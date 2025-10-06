from app.extensions import db
from app.models.voucher import VoucherOrigin


def seed_voucher_origin():
    default_voucher_origins = [
        {"name": "Office of the Mayor", "code": "1011", "keyword": "Mayor"},
        {"name": "Office of the Vice Mayor", "code": "1016", "keyword": "Vice Mayor"},
        {"name": "Sangguniang Bayan", "code": "1021", "keyword": "SB"},
        {
            "name": "Disaster Risk Reduction Office",
            "code": "9991",
            "keyword": "Disaster Office",
        },
        {
            "name": "Disaster Risk Reduction Fund",
            "code": "9992",
            "keyword": "Disaster Fund",
        },
        {"name": "Planning and Development Office", "code": "1041", "keyword": "Planning"},
        {
            "name": "Social Welfare Office",
            "code": "7611",
            "keyword": "Social Welfare",
        },
        {"name": "Agriculture Office", "code": "8711", "keyword": "Agriculture"},
        {"name": "Health Office", "code": "4411", "keyword": "Health"},
        {"name": "Engineering Office", "code": "8751", "keyword": "Engineering"},
        {"name": "Treasurer's Office (MTO)", "code": "1091", "keyword": "Treasury"},
        {"name": "Assessor's Office", "code": "1101", "keyword": "Assessor"},
        {"name": "Accounting Office", "code": "1081", "keyword": "Accounting"},
        {"name": "Civil Registrar's Office", "code": "1051", "keyword": "Registrar"},
        {"name": "Budget Office", "code": "1071", "keyword": "Budget"},
        {"name": "Environment Office", "code": "8731", "keyword": "Environment"},
        {"name": "Tourism Office", "code": "Tourism", "keyword": "Tourism"},
        {"name": "Human Resource Office", "code": "Human Resource", "keyword": "HR"},
    ]

    for vo in default_voucher_origins:
        existing = db.session.query(VoucherOrigin).filter_by(code=vo["code"]).first()
        if not existing:
            voucher_origin = VoucherOrigin(name=vo["name"], code=vo["code"], keyword=vo["keyword"])
            db.session.add(voucher_origin)

    db.session.commit()
    print("✅ Voucher origins seeded successfully.")
