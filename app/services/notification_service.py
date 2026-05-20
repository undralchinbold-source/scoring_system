from app.extensions import db
from app.models.notification import Notification
from app.utils.uuid_utils import parse_uuid


def create(data: dict) -> Notification:
    notification = Notification(
        application_id=parse_uuid(data.get("application_id")),
        channel=data["channel"],
        recipient=data["recipient"],
        subject=data.get("subject"),
        message_body=data["message_body"],
        status=data.get("status", "pending"),
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def update(notification: Notification, data: dict) -> Notification:
    for field in ("channel", "recipient", "subject", "message_body", "status", "sent_at"):
        if field in data:
            setattr(notification, field, data[field])
    db.session.commit()
    return notification


def delete(notification: Notification) -> None:
    db.session.delete(notification)
    db.session.commit()
