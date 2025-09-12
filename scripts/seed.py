import random
from datetime import datetime, timezone

from app.blueprints.auth.models import AuthIdentity
from app.blueprints.documents.models import Document, DocumentType
from app.blueprints.statuses.models import Status, StatusHistory
from app.blueprints.users.models import User
from app.extensions import db

from .rand_meta import get_random_doc_number, get_random_utc_datetime


def seed_data():
    # Create Admin User
    admin_identity = (
        db.session.query(AuthIdentity).filter_by(username="admin").first()
    )
    if not admin_identity:
        admin_user = User(full_name="Admin", role="admin", is_active=True)
        db.session.add(admin_user)
        db.session.flush()

        admin_identity = AuthIdentity(username="admin", user_id=admin_user.id)
        admin_identity.set_password("admin")
        db.session.add(admin_identity)

    # Create Staff User
    staff_identity = (
        db.session.query(AuthIdentity).filter_by(username="staff").first()
    )
    if not staff_identity:
        staff_user = User(full_name="Staff", role="staff", is_active=True)
        db.session.add(staff_user)
        db.session.flush()

        staff_identity = AuthIdentity(username="staff", user_id=staff_user.id)
        staff_identity.set_password("staff")
        db.session.add(staff_identity)

    db.session.commit()

    # Document Types
    document_types_dict = {
        "PJT": "Project",
        "SLY": "Salary",
        "OPC": "Procurement",
        "PYR": "Payroll",
        "TEV": "Travel",
        "GAS": "Gasoline",
        "TEL": "Telephone",
        "DON": "Donation",
    }

    for code, name in document_types_dict.items():
        if not db.session.query(DocumentType).filter_by(code=code).first():
            db.session.add(DocumentType(name=name, code=code))
    db.session.commit()

    # Statuses and Notes
    status_definitions = {
        "Received": "For Review",
        "Checked & Verified": "For Processing",
        "Sorted & Prepared": "For Approval",
        "Approved & Signed": "For Released",
        "Returned": "",
    }

    for name, note in status_definitions.items():
        if not db.session.query(Status).filter_by(name=name).first():
            db.session.add(Status(name=name, default_note=note))
    db.session.commit()

    # Sample Data
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

    sample_origins = [
        "Municipal Accounting Office",
        "Municipal Budget Office",
        "Municipal Health Office",
        "Municipal Engineering Office",
        "Municipal Agriculture Office",
        "Municipal Planning & Development Office",
        "Municipal Social Welfare Office",
    ]

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
    ]

    # Fetch required entities
    admin_user = db.session.query(User).filter_by(full_name="Admin").first()
    staff_user = db.session.query(User).filter_by(full_name="Staff").first()
    document_types = db.session.query(DocumentType).all()

    # Seed Documents with auto StatusHistory
    if not db.session.query(Document).first():
        received_status = (
            db.session.query(Status).filter_by(name="Received").first()
        )

        for i in range(10):
            doc = Document(
                document_type_id=random.choice(document_types).id,
                document_number=get_random_doc_number(),
                payee=random.choice(sample_payees),
                origin=random.choice(sample_origins),
                particulars=sample_particulars[i],
                amount=random.randint(1000, 50000),
                date_received=get_random_utc_datetime(days_range=30),
                status_id=received_status.id,
                created_by=staff_user.id,
            )
            db.session.add(doc)
            db.session.flush()  # Get doc.id before committing

            # Automatically log status history as "Received"
            history = StatusHistory(
                document_id=doc.id,
                status_id=received_status.id,
                changed_by=staff_user.id,
                note="For Review",
                changed_at=datetime.now(timezone.utc),
            )
            db.session.add(history)

        db.session.commit()
