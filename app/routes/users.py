import uuid
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("/")
def list_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.post("/")
def create_user():
    data = request.get_json() or {}
    required = ("email", "password", "role", "fullname")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if db.session.execute(
        db.select(User).filter_by(email=data["email"])
    ).scalar_one_or_none():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        role=data["role"],
        fullname=data["fullname"],
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.get("/<uuid:id>")
def get_user(id):
    user = db.get_or_404(User, id)
    return jsonify(user.to_dict()), 200


@bp.put("/<uuid:id>")
def update_user(id):
    user = db.get_or_404(User, id)
    data = request.get_json() or {}

    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.password_hash = generate_password_hash(data["password"])
    if "role" in data:
        user.role = data["role"]
    if "fullname" in data:
        user.fullname = data["fullname"]

    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.delete("/<uuid:id>")
def delete_user(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200
