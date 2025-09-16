from app.extensions import db
from app.models.user import Role


def seed_roles():
    dafault_user_roles = [
        {"name": "Admin", "code": "admin"},
        {"name": "Encoder", "code": "encoder"},
        {"name": "Checker", "code": "checker"},
        {"name": "Sorter", "code": "sorter"},
        {"name": "Signatory", "code": "signatory"},
    ]

    for role_data in dafault_user_roles:
        existing = db.session.query(Role).filter_by(code=role_data["code"]).first()
        if not existing:
            role = Role(name=role_data["name"], code=role_data["code"])
            db.session.add(role)

    db.session.commit()
    print("✅ Roles seeded successfully.")
