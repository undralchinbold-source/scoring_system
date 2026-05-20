from datetime import datetime, timezone

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.user import User


def find_user_by_email(email: str) -> User | None:
    return db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()


def verify_password(user: User, password: str) -> bool:
    return check_password_hash(user.password_hash, password)


def login(email: str, password: str) -> dict | None:
    user = find_user_by_email(email)
    if not user or not verify_password(user, password):
        return None

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email},
    )
    return {"access_token": access_token, "user": user.to_dict()}
