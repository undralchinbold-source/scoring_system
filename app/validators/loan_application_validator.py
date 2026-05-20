from http import HTTPStatus
from flask import jsonify

ALLOWED_STATUSES = {"pending", "approved", "rejected", "cancelled"}


def validate_create(data: dict):
    required = ("client_id", "requested_amount")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST
    return None


def validate_status(status: str):
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": f"Invalid status. Choose from: {ALLOWED_STATUSES}"}), HTTPStatus.BAD_REQUEST
    return None
