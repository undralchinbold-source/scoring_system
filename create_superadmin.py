from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()

    email = "admin@local.mn"
    password = "Admin@1234"

    existing = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if existing:
        print(f"Аль хэдийн үүссэн байна: {email}")
    else:
        user = User(
            email=email,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            role="super_user",
            fullname="Super Admin",
        )
        db.session.add(user)
        db.session.commit()
        print(f"Амжилттай үүслээ!")
        print(f"  Email   : {email}")
        print(f"  Password: {password}")
        print(f"  Role    : super_user")
