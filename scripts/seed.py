from app.blueprints.users import models
from app.extensions import db


def seed_data():
    if not db.session.execute(db.select(models.User).filter_by(username="admin")).scalar_one_or_none():
        admin = models.User(full_name="Administrator", role="admin", username="admin")
        admin.set_password("admin")
        db.session.add(admin)
    db.session.commit()
