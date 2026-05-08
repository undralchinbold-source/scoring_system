import uuid
from datetime import datetime, timezone
from app.extensions import db


class LoanApplication(db.Model):
    __tablename__ = "loan_applications"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.clients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    client = db.relationship("Client", back_populates="loan_applications")
    user = db.relationship("User", back_populates="loan_applications")
    score_histories = db.relationship(
        "ScoreHistory", back_populates="application", lazy="dynamic"
    )
    notifications = db.relationship(
        "Notification", back_populates="application", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "requested_amount": float(self.requested_amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<LoanApplication {self.id} status={self.status}>"
