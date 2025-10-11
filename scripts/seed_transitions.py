from app.extensions import db
from app.models.user import Role
from app.models.voucher import VoucherStatus, VoucherStatusTransition


def seed_transitions():
    # Status query
    received = VoucherStatus.query.filter_by(code="received").one()
    checked = VoucherStatus.query.filter_by(code="checked").one()
    sorted_ = VoucherStatus.query.filter_by(code="sorted").one()
    approved = VoucherStatus.query.filter_by(code="approved").one()
    returned = VoucherStatus.query.filter_by(code="returned").one()

    # Roles query
    admin = Role.query.filter_by(code="admin").one()
    encoder = Role.query.filter_by(code="encoder").one()
    checker = Role.query.filter_by(code="checker").one()
    sorter = Role.query.filter_by(code="sorter").one()
    approver = Role.query.filter_by(code="approver").one()

    db.session.add_all(
        [
            # Ideal voucher workflow (received → checked → sorted → approved)
            VoucherStatusTransition(from_status=received, to_status=checked, allowed_roles=[checker]),
            VoucherStatusTransition(from_status=checked, to_status=sorted_, allowed_roles=[sorter]),
            VoucherStatusTransition(from_status=sorted_, to_status=approved, allowed_roles=[approver]),
            # With incomplete voucher attachments/requirements (received → returned / sorted → returned)
            VoucherStatusTransition(from_status=received, to_status=returned, allowed_roles=[checker]),
            VoucherStatusTransition(from_status=sorted_, to_status=returned, allowed_roles=[approver]),
            # Voucher already in the system (returned → received)
            VoucherStatusTransition(from_status=returned, to_status=received, allowed_roles=[encoder]),
            # Admin privileges (ideal)
            VoucherStatusTransition(from_status=received, to_status=checked, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=checked, to_status=sorted_, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=sorted_, to_status=approved, allowed_roles=[admin]),
            # Admin privileges (returned)
            VoucherStatusTransition(from_status=received, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=checked, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=sorted_, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=approved, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=returned, to_status=received, allowed_roles=[admin]),
        ]
    )
    db.session.commit()
