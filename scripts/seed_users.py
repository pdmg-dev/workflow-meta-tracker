from app.extensions import db
from app.models.user import Role, User


def seed_users():
    default_users = [
        {
            "full_name": "Philip Daniel M. Gonzales",
            "roles": ["admin"],
            "username": "philip",
            "password": "philip",
        },
        {
            "full_name": "Shane F. Tunzon",
            "roles": ["admin, encoder", "checker", "sorter", "approver"],
            "username": "shane",
            "password": "shane",
        },
        {"full_name": "Revilyn D. Rosas", "roles": ["checker", "sorter"], "username": "ivy", "password": "ivy"},
        {"full_name": "Christine H. Ayuso", "roles": ["checker"], "username": "tin", "password": "tin"},
        {"full_name": "Cecilia I. Palmes", "roles": ["checker"], "username": "cecil", "password": "cecil"},
        {"full_name": "Maureen F. Alapaap", "roles": ["checker"], "username": "mau", "password": "mau"},
        {"full_name": "Jade Aniel S. Bonaobra", "roles": ["checker"], "username": "jade", "password": "jade"},
    ]

    role_codes = {code for user in default_users for code in user["roles"]}
    existing_roles = {r.code: r for r in db.session.query(Role).filter(Role.code.in_(role_codes)).all()}

    for code in role_codes:
        if code not in existing_roles:
            role = Role(code=code, name=code.capitalize())
            db.session.add(role)
            existing_roles[code] = role
    db.session.flush()

    existing_usernames = {u.username for u in db.session.query(User.username).all()}

    for user_data in default_users:
        if user_data["username"] in existing_usernames:
            continue
        user = User(full_name=user_data["full_name"], username=user_data["username"])
        user.set_password(user_data["password"])
        user.roles = [existing_roles[code] for code in user_data["roles"]]
        db.session.add(user)

    db.session.commit()
    print("✅ Users seeded successfully.")
