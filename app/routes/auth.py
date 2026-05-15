from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email},
    )

    return jsonify({
        "access_token": access_token,
        "user": user.to_dict(),
    }), 200
