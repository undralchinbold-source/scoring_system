from app.extensions import db
from app.models.audit_log import AuditLog
from app.utils.uuid_utils import parse_uuid


def create(data: dict) -> AuditLog:
    log = AuditLog(
        user_id=parse_uuid(data.get("user_id")),
        action=data["action"],
        entity_type=data["entity_type"],
        entity_id=parse_uuid(data.get("entity_id")),
    )
    db.session.add(log)
    db.session.commit()
    return log


def update(log: AuditLog, data: dict) -> AuditLog:
    if "action" in data:
        log.action = data["action"]
    if "entity_type" in data:
        log.entity_type = data["entity_type"]
    if "entity_id" in data:
        log.entity_id = parse_uuid(data.get("entity_id"))
    db.session.commit()
    return log


def delete(log: AuditLog) -> None:
    db.session.delete(log)
    db.session.commit()
