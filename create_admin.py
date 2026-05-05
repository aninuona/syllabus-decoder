# Run once to pre-authorize admin emails
# admin will set their own password the first time they log in

from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    email = input("Enter the email to authorize as admin: ").strip().lower()

    if User.query.filter_by(email=email).first():
        print(f"{email} is already in the system.")
    else:
        # DB requires password_hash NOT NULL, so store a value indicting "needs password set". auth.py will prompt the admin to create a password on first login.
        # auth.py treats "UNSET" (not a valid bcrypt hash) as no password, and will prompt the admin to create one on first login.
        u = User(email=email, password_hash="UNSET", role="admin")
        db.session.add(u)
        db.session.commit()
        print(f"Authorized {email}. They can now log in at /login and set their password.")
