import uuid
from datetime import datetime, timezone
from app.extensions import db


class ScoreHistory(db.Model):
    __tablename__ = "score_history"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.loan_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_version = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Numeric(10, 4), nullable=False)
    decision = db.Column(db.String(50), nullable=False)
    created_by = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    application = db.relationship("LoanApplication", back_populates="score_histories")
    created_by_user = db.relationship("User", back_populates="scores_created")

    def to_dict(self):
        return {
            "id": str(self.id),
            "application_id": str(self.application_id),
            "model_version": self.model_version,
            "score": float(self.score),
            "decision": self.decision,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ScoreHistory app={self.application_id} score={self.score} decision={self.decision}>"
