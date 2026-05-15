from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.user import User
from app.auth import create_token
from app.utils.response import missing_fields_error

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = request.get_json() or {}
    required = ("email", "password", "fullname", "role")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return missing_fields_error(missing)

    if data["role"] not in ("super_user", "admin"):
        return jsonify({"error": "Role must be 'super_user' or 'admin'"}), 400

    if db.session.execute(
        db.select(User).filter_by(email=data["email"])
    ).scalar_one_or_none():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        fullname=data["fullname"],
        role=data["role"],
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"token": create_token(user), "user": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"token": create_token(user), "user": user.to_dict()}), 200
