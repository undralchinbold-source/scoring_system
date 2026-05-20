from http import HTTPStatus
from flask import jsonify
from app.utils.decorators import VALID_ROLES


def validate_create(data: dict):
    required = ("email", "password", "role", "fullname")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST
    return validate_role(data["role"])


def validate_role(role: str):
    if role not in VALID_ROLES:
        return jsonify({"error": "role must be 'admin' or 'super_user'"}), HTTPStatus.BAD_REQUEST
    return None
