from __future__ import annotations

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User


def find_by_email(email: str) -> User | None:
    return db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()


def create(data: dict) -> User:
    user = User(
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        role=data["role"],
        fullname=data["fullname"],
    )
    db.session.add(user)
    db.session.commit()
    return user


def update(user: User, data: dict) -> User:
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.password_hash = generate_password_hash(data["password"])
    if "role" in data:
        user.role = data["role"]
    if "fullname" in data:
        user.fullname = data["fullname"]
    db.session.commit()
    return user


def delete(user: User) -> None:
    db.session.delete(user)
    db.session.commit()
