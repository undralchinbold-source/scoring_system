from app.extensions import db
from app.models.score_history import ScoreHistory
from app.utils.uuid_utils import parse_uuid


def create(data: dict) -> ScoreHistory:
    record = ScoreHistory(
        application_id=parse_uuid(data["application_id"]),
        model_version=data["model_version"],
        score=data["score"],
        decision=data["decision"],
        created_by=parse_uuid(data.get("created_by")),
    )
    db.session.add(record)
    db.session.commit()
    return record


def update(record: ScoreHistory, data: dict) -> ScoreHistory:
    if "model_version" in data:
        record.model_version = data["model_version"]
    if "score" in data:
        record.score = data["score"]
    if "decision" in data:
        record.decision = data["decision"]
    db.session.commit()
    return record


def delete(record: ScoreHistory) -> None:
    db.session.delete(record)
    db.session.commit()
