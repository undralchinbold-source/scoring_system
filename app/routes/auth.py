from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.validators import auth_validator
from app.services import auth_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    data = request.get_json() or {}
    err = auth_validator.validate_login(data)
    if err:
        return err

    result = auth_service.login(
        email=data.get("email", "").strip(),
        password=data.get("password", ""),
    )
    if not result:
        return jsonify({"error": "Invalid email or password"}), HTTPStatus.UNAUTHORIZED

    return jsonify(result), HTTPStatus.OK
