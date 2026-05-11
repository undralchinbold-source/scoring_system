import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from app.extensions import db
from app.models.user import User

VALID_ROLES = {"super_user", "admin"}


def create_token(user):
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Authorization header required"}), 401
            token = auth_header.split(" ", 1)[1]
            try:
                payload = jwt.decode(
                    token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            if payload.get("role") not in allowed_roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403

            user = db.session.get(User, payload["sub"])
            if not user:
                return jsonify({"error": "User not found"}), 401

            request.current_user = user
            return f(*args, **kwargs)

        return decorated

    return decorator


# Shortcuts
both_roles = require_role("super_user", "admin")
super_only = require_role("super_user")
