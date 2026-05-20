import pytest
from app import create_app
from app.extensions import db as _db


class TestConfig:
    TESTING = True
    # PostgreSQL "public" schema-г SQLite-д None (default) руу map хийнэ
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "execution_options": {"schema_translate_map": {"public": None}}
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-minimum-32-bytes-long!!"
    SECRET_KEY = "test-secret-key-minimum-32-bytes-long!!"


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config.from_object(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    yield _db
    _db.session.rollback()


@pytest.fixture
def admin_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(
            identity="00000000-0000-0000-0000-000000000001",
            additional_claims={"role": "admin", "email": "admin@test.com"},
        )


@pytest.fixture
def super_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(
            identity="00000000-0000-0000-0000-000000000002",
            additional_claims={"role": "super_user", "email": "super@test.com"},
        )


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_fixture(db):
    from werkzeug.security import generate_password_hash
    from app.models.user import User
    user = User(
        email="testuser@example.com",
        password_hash=generate_password_hash("correct-password"),
        role="admin",
        fullname="Test User",
    )
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    yield user
    existing = db.session.get(User, user_id)
    if existing:
        db.session.delete(existing)
        db.session.commit()


@pytest.fixture
def client_fixture(db):
    from app.models.client import Client
    c = Client(national_id="AA12345678", fullname="Test Client")
    db.session.add(c)
    db.session.commit()
    cid = c.id
    yield c
    existing = db.session.get(Client, cid)
    if existing:
        db.session.delete(existing)
        db.session.commit()


@pytest.fixture
def loan_app_fixture(db, client_fixture):
    from app.models.loan_application import LoanApplication
    loan = LoanApplication(
        client_id=client_fixture.id,
        requested_amount=5_000_000,
        status="pending",
    )
    db.session.add(loan)
    db.session.commit()
    lid = loan.id
    yield loan
    existing = db.session.get(LoanApplication, lid)
    if existing:
        db.session.delete(existing)
        db.session.commit()


@pytest.fixture
def notification_fixture(db, loan_app_fixture):
    from app.models.notification import Notification
    n = Notification(
        application_id=loan_app_fixture.id,
        channel="email",
        recipient="test@example.com",
        message_body="Test message",
    )
    db.session.add(n)
    db.session.commit()
    nid = n.id
    yield n
    existing = db.session.get(Notification, nid)
    if existing:
        db.session.delete(existing)
        db.session.commit()


@pytest.fixture
def score_history_fixture(db, loan_app_fixture):
    from app.models.score_history import ScoreHistory
    s = ScoreHistory(
        application_id=loan_app_fixture.id,
        model_version="v1.0.0",
        score=750,
        decision="approved",
    )
    db.session.add(s)
    db.session.commit()
    sid = s.id
    yield s
    existing = db.session.get(ScoreHistory, sid)
    if existing:
        db.session.delete(existing)
        db.session.commit()


@pytest.fixture
def audit_log_fixture(db):
    from app.models.audit_log import AuditLog
    log = AuditLog(action="test_action", entity_type="User")
    db.session.add(log)
    db.session.commit()
    log_id = log.id
    yield log
    existing = db.session.get(AuditLog, log_id)
    if existing:
        db.session.delete(existing)
        db.session.commit()
