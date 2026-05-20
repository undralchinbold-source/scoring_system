from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils.decorators import any_role_required, super_user_required
from app.validators import audit_log_validator
from app.services import audit_log_service

bp = Blueprint("audit_logs", __name__, url_prefix="/api/audit-logs")


@bp.get("/")
@any_role_required
def list_audit_logs():
    logs = db.session.execute(db.select(AuditLog)).scalars().all()
    return jsonify([l.to_dict() for l in logs]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_audit_log():
    data = request.get_json() or {}
    err = audit_log_validator.validate_create(data)
    if err:
        return err
    log = audit_log_service.create(data)
    return jsonify(log.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    return jsonify(log.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    data = request.get_json() or {}
    log = audit_log_service.update(log, data)
    return jsonify(log.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    audit_log_service.delete(log)
    return jsonify({"message": "Audit log deleted"}), HTTPStatus.OK
