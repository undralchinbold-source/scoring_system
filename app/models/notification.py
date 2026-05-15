import uuid
from datetime import datetime, timezone
from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.loan_applications.id", ondelete="CASCADE"),
        nullable=True,
    )
    channel = db.Column(db.String(50), nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message_body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)

    application = db.relationship("LoanApplication", back_populates="notifications")

    def to_dict(self):
        return {
            "id": str(self.id),
            "application_id": str(self.application_id) if self.application_id else None,
            "channel": self.channel,
            "recipient": self.recipient,
            "subject": self.subject,
            "message_body": self.message_body,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }

    def __repr__(self):
        return f"<Notification channel={self.channel} recipient={self.recipient} status={self.status}>"
