from app.blueprints.auth.models import AuthIdentity
from app.blueprints.users.models import User
from app.extensions import db


def seed_data():
    existing_identity = db.session.execute(
        db.select(AuthIdentity).filter_by(username="admin")
    ).scalar_one_or_none()

    if not existing_identity:
        admin_user = User(
            full_name="Administrator", role="admin", is_active=True
        )
        db.session.add(admin_user)
        db.session.flush()

        admin_identity = AuthIdentity(username="admin", user_id=admin_user.id)
        admin_identity.set_password("admin")
        db.session.add(admin_identity)

    db.session.commit()
