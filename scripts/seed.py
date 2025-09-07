from app.blueprints.auth.models import AuthIdentity
from app.blueprints.documents.models import DocumentType
from app.blueprints.users.models import User
from app.extensions import db


def seed_data():
    # Admin User
    existing_identity = db.session.execute(
        db.session.query(AuthIdentity).filter_by(username="admin")
    ).first()

    if not existing_identity:
        admin_user = User(full_name="Admin", role="admin", is_active=True)
        db.session.add(admin_user)
        db.session.flush()

        admin_identity = AuthIdentity(username="admin", user_id=admin_user.id)
        admin_identity.set_password("admin")
        db.session.add(admin_identity)

    # Staff User
    existing_identity = db.session.execute(
        db.session.query(AuthIdentity).filter_by(username="staff")
    ).first()

    if not existing_identity:
        staff_user = User(full_name="Staff", role="staff", is_active=True)
        db.session.add(staff_user)
        db.session.flush()

        staff_identity = AuthIdentity(username="staff", user_id=staff_user.id)
        staff_identity.set_password("staff")
        db.session.add(staff_identity)

    db.session.commit()

    # Document Types
    document_types = {
        "DBV": "Disbursement Voucher",
        "PYR": "Payroll",
        "PO": "Purchase Order",
        "PR": "Purchase Request",
        "OR": "Official Receipt",
        "LQR": "Liquidation Reports",
    }

    for code, name in document_types.items():
        if not db.session.query(DocumentType).filter_by(code=code).first():
            db.session.add(DocumentType(name=name, code=code))
    db.session.commit()
