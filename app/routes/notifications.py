import uuid
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.notification import Notification

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@bp.get("/")
def list_notifications():
    items = db.session.execute(db.select(Notification)).scalars().all()
    return jsonify([n.to_dict() for n in items]), 200


@bp.post("/")
def create_notification():
    data = request.get_json() or {}
    required = ("channel", "recipient", "message_body")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

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
def get_notification(id):
    notification = db.get_or_404(Notification, id)
    return jsonify(notification.to_dict()), 200


@bp.put("/<uuid:id>")
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
def delete_notification(id):
    notification = db.get_or_404(Notification, id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "Notification deleted"}), 200
