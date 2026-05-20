from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.notification import Notification
from app.utils.decorators import any_role_required, super_user_required
from app.validators import notification_validator
from app.services import notification_service

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@bp.get("/")
@any_role_required
def list_notifications():
    items = db.session.execute(db.select(Notification)).scalars().all()
    return jsonify([n.to_dict() for n in items]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_notification():
    data = request.get_json() or {}
    err = notification_validator.validate_create(data)
    if err:
        return err
    notification = notification_service.create(data)
    return jsonify(notification.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_notification(id):
    notification = db.get_or_404(Notification, id)
    return jsonify(notification.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_notification(id):
    notification = db.get_or_404(Notification, id)
    data = request.get_json() or {}
    notification = notification_service.update(notification, data)
    return jsonify(notification.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_notification(id):
    notification = db.get_or_404(Notification, id)
    notification_service.delete(notification)
    return jsonify({"message": "Notification deleted"}), HTTPStatus.OK
