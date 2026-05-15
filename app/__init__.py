import os
from flask import Flask
from config import config_by_name
from app.extensions import db, migrate


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from app.models import (  # noqa: F401
        User,
        Client,
        LoanApplication,
        AuditLog,
        ScoreHistory,
        Notification,
    )

    from app.routes import (
        auth_bp,
        users_bp,
        clients_bp,
        loan_applications_bp,
        audit_logs_bp,
        score_history_bp,
        notifications_bp,
        predict_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(loan_applications_bp)
    app.register_blueprint(audit_logs_bp)
    app.register_blueprint(score_history_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(predict_bp)

    return app
