import random

from app.blueprints.auth.models import AuthIdentity
from app.blueprints.documents.models import Document, DocumentType
from app.blueprints.statuses.models import Status
from app.blueprints.users.models import User
from app.extensions import db

from .rand_meta import get_random_doc_number, get_random_utc_datetime


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

    # Statuses
    for name in ["Received", "Processing", "Released"]:
        if not db.session.query(Status).filter_by(name=name).first():
            db.session.add(Status(name=name))
    db.session.commit()

    # Sample "Payees"
    sample_payees = [
        "Liam Reyes",
        "Isabella Cruz",
        "Mateo Nakamura",
        "Aaliyah Santiago",
        "Noah Villanueva",
        "Sofia Tanaka",
        "Elijah Mendoza",
        "Chloe Ramirez",
        "Kai Navarro",
        "Zara Delos Santos",
    ]

    # Sample "Origin"
    sample_origins = [
        "Municipal Accounting Office",
        "Municipal Budget Office",
        "Municipal Health Office",
        "Municipal Engineering Office",
        "Municipal Agriculture Office",
        "Municipal Planning & Development Office",
        "Municipal Social Welfare Office",
    ]

    # Sample "Particulars"
    sample_particulars = [
        "Payment for barangay health workers' honorarium - Q3 2025",
        "Procurement of construction materials for covered court in Brgy. Poblacion",  # noqa: E501
        "Reimbursement for travel expenses during regional budget consultation",  # noqa: E501
        "Purchase of office supplies for Municipal Treasurer's Office",
        "Salary disbursement for job order personnel - August 2025",
        "Payment for catering services during Nutrition Month celebration",
        "Repair and maintenance of municipal service vehicle",
        "Printing of official receipts for local business tax collection",
        "Purchase of agricultural inputs for farmers' livelihood program",
        "Consultancy fee for urban planning project - Phase 1",
        "Fuel expenses for disaster response operations",
        "Rental of sound system for Independence Day program",
        "Medical supplies for Municipal Health Office",
        "Honorarium for guest speaker during Youth Leadership Summit",
        "Internet service payment for Municipal Hall - September 2025",
    ]

    # Query for documents
    admin = db.session.query(AuthIdentity).filter_by(username="admin").first()
    staff = db.session.query(AuthIdentity).filter_by(username="staff").first()
    document_types = db.session.query(DocumentType).all()
    statuses = db.session.query(Status).all()

    # Documents
    if not Document.query.first():
        for i in range(10):
            doc = Document(
                document_type_id=random.choice(document_types).id,
                document_number=get_random_doc_number(),
                payee=random.choice(sample_payees),
                origin=random.choice(sample_origins),
                particulars=sample_particulars[i],
                amount=random.randint(1000, 50000),
                date_received=get_random_utc_datetime(days_range=30),
                status_id=random.choice(statuses).id,
                created_by=random.choice([admin.id, staff.id]),
            )
            db.session.add(doc)
            db.session.flush()
        db.session.commit()
