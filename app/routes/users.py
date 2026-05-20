from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.user import User
from app.utils.decorators import any_role_required, super_user_required
from app.validators import user_validator
from app.services import user_service

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("/")
@any_role_required
def list_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([u.to_dict() for u in users]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_user():
    data = request.get_json() or {}
    err = user_validator.validate_create(data)
    if err:
        return err
    if user_service.find_by_email(data["email"]):
        return jsonify({"error": "Email already exists"}), HTTPStatus.CONFLICT
    user = user_service.create(data)
    return jsonify(user.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_user(id):
    user = db.get_or_404(User, id)
    return jsonify(user.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_user(id):
    user = db.get_or_404(User, id)
    data = request.get_json() or {}
    if "role" in data:
        err = user_validator.validate_role(data["role"])
        if err:
            return err
    user = user_service.update(user, data)
    return jsonify(user.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_user(id):
    user = db.get_or_404(User, id)
    user_service.delete(user)
    return jsonify({"message": "User deleted"}), HTTPStatus.OK
