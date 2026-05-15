import uuid
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.audit_log import AuditLog
from app.utils.decorators import any_role_required, super_user_required

bp = Blueprint("audit_logs", __name__, url_prefix="/api/audit-logs")


@bp.get("/")
@any_role_required
def list_audit_logs():
    logs = db.session.execute(db.select(AuditLog)).scalars().all()
    return jsonify([l.to_dict() for l in logs]), 200


@bp.post("/")
@super_user_required
def create_audit_log():
    data = request.get_json() or {}
    required = ("action", "entity_type")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    log = AuditLog(
        user_id=uuid.UUID(data["user_id"]) if data.get("user_id") else None,
        action=data["action"],
        entity_type=data["entity_type"],
        entity_id=uuid.UUID(data["entity_id"]) if data.get("entity_id") else None,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(log.to_dict()), 201


@bp.get("/<uuid:id>")
@any_role_required
def get_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    return jsonify(log.to_dict()), 200


@bp.put("/<uuid:id>")
@super_user_required
def update_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    data = request.get_json() or {}

    if "action" in data:
        log.action = data["action"]
    if "entity_type" in data:
        log.entity_type = data["entity_type"]
    if "entity_id" in data:
        log.entity_id = uuid.UUID(data["entity_id"]) if data["entity_id"] else None

    db.session.commit()
    return jsonify(log.to_dict()), 200


@bp.delete("/<uuid:id>")
@super_user_required
def delete_audit_log(id):
    log = db.get_or_404(AuditLog, id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Audit log deleted"}), 200
