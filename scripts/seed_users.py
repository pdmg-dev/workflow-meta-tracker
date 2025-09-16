from app.extensions import db
from app.models.user import Role, User


def seed_users():
    default_users = [
        {"full_name": "Shane", "roles": ["signatory"], "username": "shane", "password": "shane"},
        {"full_name": "Tin", "roles": ["checker"], "username": "tin", "password": "tin"},
        {"full_name": "Cecil", "roles": ["checker"], "username": "cecil", "password": "cecil"},
        {"full_name": "Ivy", "roles": ["checker", "sorter"], "username": "ivy", "password": "ivy"},
        {"full_name": "Mau", "roles": ["checker"], "username": "mau", "password": "mau"},
        {"full_name": "Jade", "roles": ["checker"], "username": "jade", "password": "jade"},
        {"full_name": "System Administrator", "roles": ["admin"], "username": "admin", "password": "admin"},
        {
            "full_name": "Philip",
            "roles": ["encoder", "checker", "sorter", "signatory"],
            "username": "philip",
            "password": "philip",
        },
    ]

    # Create roles if they don't exist
    role_codes = {code for user in default_users for code in user["roles"]}
    existing_roles = {r.code: r for r in db.session.query(Role).filter(Role.code.in_(role_codes)).all()}

    for code in role_codes:
        if code not in existing_roles:
            role = Role(code=code, name=code.capitalize())
            db.session.add(role)
            existing_roles[code] = role

    db.session.flush()  # Ensure roles have IDs before assigning

    # Create users if they don't exist
    existing_usernames = {u.username for u in db.session.query(User.username).all()}

    for user_data in default_users:
        if user_data["username"] in existing_usernames:
            continue  # Skip existing user

        user = User(full_name=user_data["full_name"], username=user_data["username"])
        user.set_password(user_data["password"])
        user.roles = [existing_roles[code] for code in user_data["roles"]]
        db.session.add(user)

    db.session.commit()
    print("✅ Users seeded successfully.")
