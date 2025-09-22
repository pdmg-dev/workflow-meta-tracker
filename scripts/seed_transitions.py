from app.extensions import db
from app.models.user import Role
from app.models.voucher import VoucherStatus, VoucherStatusTransition


def seed_transitions():
    received = VoucherStatus.query.filter_by(code="received").one()
    checked = VoucherStatus.query.filter_by(code="checked").one()
    sorted_ = VoucherStatus.query.filter_by(code="sorted").one()
    approved = VoucherStatus.query.filter_by(code="approved").one()
    returned = VoucherStatus.query.filter_by(code="returned").one()

    checker = Role.query.filter_by(code="checker").one()
    sorter = Role.query.filter_by(code="sorter").one()
    approver = Role.query.filter_by(code="signatory").one()
    admin = Role.query.filter_by(code="admin").one()  # for example
    manager = Role.query.filter_by(code="manager").one()  # for example

    db.session.add_all(
        [
            # normal forward flow
            VoucherStatusTransition(from_status=received, to_status=checked, allowed_roles=[checker]),
            VoucherStatusTransition(from_status=checked, to_status=sorted_, allowed_roles=[sorter]),
            VoucherStatusTransition(from_status=sorted_, to_status=approved, allowed_roles=[approver]),
            # return path – allow from every step back to returned
            VoucherStatusTransition(from_status=received, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=checked, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=sorted_, to_status=returned, allowed_roles=[admin]),
            VoucherStatusTransition(from_status=approved, to_status=returned, allowed_roles=[admin]),
            # return path – allow from every step back to returned
            VoucherStatusTransition(from_status=received, to_status=returned, allowed_roles=[manager]),
            VoucherStatusTransition(from_status=checked, to_status=returned, allowed_roles=[manager]),
            VoucherStatusTransition(from_status=sorted_, to_status=returned, allowed_roles=[manager]),
            VoucherStatusTransition(from_status=approved, to_status=returned, allowed_roles=[manager]),
        ]
    )
    db.session.commit()
