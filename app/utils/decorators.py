import uuid
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

VALID_ROLES = frozenset({"admin", "super_user"})


def current_user_id() -> uuid.UUID:
    return uuid.UUID(get_jwt_identity())


def validate_required(data: dict, fields) -> list:
    return [f for f in fields if data.get(f) is None]


def _get_role():
    return get_jwt().get("role")


def any_role_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if _get_role() not in VALID_ROLES:
            return jsonify({"error": "Access forbidden: insufficient role"}), 403
        return fn(*args, **kwargs)
    return wrapper


def super_user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if _get_role() != "super_user":
            return jsonify({"error": "Access forbidden: super_user role required"}), 403
        return fn(*args, **kwargs)
    return wrapper
