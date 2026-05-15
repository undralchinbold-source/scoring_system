import uuid
from datetime import datetime, timezone
from app.extensions import db


class Client(db.Model):
    __tablename__ = "clients"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    income = db.Column(db.Numeric(15, 2), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
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

    created_by_user = db.relationship("User", back_populates="clients_created")
    loan_applications = db.relationship(
        "LoanApplication", back_populates="client", lazy="dynamic", passive_deletes=True
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "national_id": self.national_id,
            "fullname": self.fullname,
            "income": float(self.income) if self.income is not None else None,
            "phone": self.phone,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Client {self.national_id} - {self.fullname}>"
