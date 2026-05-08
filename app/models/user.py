import uuid
from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    audit_logs = db.relationship("AuditLog", back_populates="user", lazy="dynamic")
    loan_applications = db.relationship(
        "LoanApplication", back_populates="user", lazy="dynamic"
    )
    clients_created = db.relationship(
        "Client", back_populates="created_by_user", lazy="dynamic"
    )
    scores_created = db.relationship(
        "ScoreHistory", back_populates="created_by_user", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "role": self.role,
            "fullname": self.fullname,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"
