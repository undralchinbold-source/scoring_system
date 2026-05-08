from .users import bp as users_bp
from .clients import bp as clients_bp
from .loan_applications import bp as loan_applications_bp
from .audit_logs import bp as audit_logs_bp
from .score_history import bp as score_history_bp
from .notifications import bp as notifications_bp

__all__ = [
    "users_bp",
    "clients_bp",
    "loan_applications_bp",
    "audit_logs_bp",
    "score_history_bp",
    "notifications_bp",
]
