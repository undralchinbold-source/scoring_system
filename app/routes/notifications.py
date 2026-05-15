import uuid
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.notification import Notification
from app.auth import both_roles, super_only
from app.utils.response import missing_fields_error

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@bp.get("/")
@both_roles
def list_notifications():
    items = db.session.execute(db.select(Notification)).scalars().all()
    return jsonify([n.to_dict() for n in items]), 200


@bp.post("/")
@super_only
def create_notification():
    data = request.get_json() or {}
    required = ("channel", "recipient", "message_body")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return missing_fields_error(missing)

    notification = Notification(
        application_id=uuid.UUID(data["application_id"]) if data.get("application_id") else None,
        channel=data["channel"],
        recipient=data["recipient"],
        subject=data.get("subject"),
        message_body=data["message_body"],
        status=data.get("status", "pending"),
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification.to_dict()), 201


@bp.get("/<uuid:id>")
@both_roles
def get_notification(id):
    notification = db.get_or_404(Notification, id)
    return jsonify(notification.to_dict()), 200


@bp.put("/<uuid:id>")
@super_only
def update_notification(id):
    notification = db.get_or_404(Notification, id)
    data = request.get_json() or {}

    if "channel" in data:
        notification.channel = data["channel"]
    if "recipient" in data:
        notification.recipient = data["recipient"]
    if "subject" in data:
        notification.subject = data["subject"]
    if "message_body" in data:
        notification.message_body = data["message_body"]
    if "status" in data:
        notification.status = data["status"]
    if "sent_at" in data:
        notification.sent_at = data["sent_at"]

    db.session.commit()
    return jsonify(notification.to_dict()), 200


@bp.delete("/<uuid:id>")
@super_only
def delete_notification(id):
    notification = db.get_or_404(Notification, id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "Notification deleted"}), 200
