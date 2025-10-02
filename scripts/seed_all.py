from .seed_fund import seed_funds
from .seed_origin import seed_voucher_origin
from .seed_roles import seed_roles
from .seed_statuses import seed_statuses
from .seed_transitions import seed_transitions
from .seed_types import seed_voucher_types
from .seed_users import seed_users


def seed_all():
    seed_roles()
    seed_users()
    seed_voucher_types()
    seed_statuses()
    seed_transitions()
    seed_voucher_origin()
    seed_funds()


if __name__ == "__main__":
    seed_all()
