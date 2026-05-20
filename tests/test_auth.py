class TestLogin:
    """POST /api/auth/login"""

    def test_login_success(self, client, user_fixture):
        res = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "correct-password",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "testuser@example.com"

    def test_login_returns_user_fields(self, client, user_fixture):
        res = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "correct-password",
        })
        user = res.get_json()["user"]
        assert "id" in user
        assert "email" in user
        assert "role" in user
        assert "fullname" in user
        assert "password_hash" not in user

    def test_login_updates_last_login(self, client, db, user_fixture):
        from app.models.user import User
        client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "correct-password",
        })
        db.session.expire(user_fixture)
        user = db.session.get(User, user_fixture.id)
        assert user.last_login is not None

    def test_wrong_password_returns_401(self, client, user_fixture):
        res = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "wrong-password",
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_nonexistent_email_returns_401(self, client):
        res = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "any-password",
        })
        assert res.status_code == 401

    def test_missing_email_returns_400(self, client):
        res = client.post("/api/auth/login", json={"password": "correct-password"})
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_missing_password_returns_400(self, client):
        res = client.post("/api/auth/login", json={"email": "testuser@example.com"})
        assert res.status_code == 400

    def test_empty_body_returns_400(self, client):
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 400

    def test_whitespace_email_returns_400(self, client):
        res = client.post("/api/auth/login", json={
            "email": "   ",
            "password": "correct-password",
        })
        assert res.status_code == 400

    def test_email_is_trimmed(self, client, user_fixture):
        res = client.post("/api/auth/login", json={
            "email": "  testuser@example.com  ",
            "password": "correct-password",
        })
        assert res.status_code == 200

    def test_no_json_body_returns_4xx(self, client):
        # JSON Content-Type байхгүй бол Flask 415 буцаана
        res = client.post("/api/auth/login")
        assert res.status_code in (400, 415)


class TestAuthValidator:
    """app/validators/auth_validator.py"""

    def test_valid_data_returns_none(self, client):
        from app.validators.auth_validator import validate_login
        # client fixture ensures app context is active
        with client.application.app_context():
            result = validate_login({"email": "a@b.com", "password": "secret"})
            assert result is None

    def test_missing_email_returns_tuple(self, client):
        from app.validators.auth_validator import validate_login
        with client.application.app_context():
            response, status = validate_login({"password": "secret"})
            assert status == 400

    def test_missing_password_returns_tuple(self, client):
        from app.validators.auth_validator import validate_login
        with client.application.app_context():
            response, status = validate_login({"email": "a@b.com"})
            assert status == 400

    def test_whitespace_email_fails(self, client):
        from app.validators.auth_validator import validate_login
        with client.application.app_context():
            result = validate_login({"email": "   ", "password": "secret"})
            assert result is not None


class TestAuthService:
    """app/services/auth_service.py"""

    def test_find_user_by_email_found(self, user_fixture):
        from app.services.auth_service import find_user_by_email
        user = find_user_by_email("testuser@example.com")
        assert user is not None
        assert user.email == "testuser@example.com"

    def test_find_user_by_email_not_found(self, db):
        from app.services.auth_service import find_user_by_email
        user = find_user_by_email("nobody@example.com")
        assert user is None

    def test_verify_password_correct(self, user_fixture):
        from app.services.auth_service import verify_password
        assert verify_password(user_fixture, "correct-password") is True

    def test_verify_password_wrong(self, user_fixture):
        from app.services.auth_service import verify_password
        assert verify_password(user_fixture, "wrong-password") is False

    def test_login_returns_token_and_user(self, user_fixture):
        from app.services.auth_service import login
        result = login("testuser@example.com", "correct-password")
        assert result is not None
        assert "access_token" in result
        assert "user" in result

    def test_login_wrong_credentials_returns_none(self, user_fixture):
        from app.services.auth_service import login
        result = login("testuser@example.com", "wrong-password")
        assert result is None

    def test_login_unknown_email_returns_none(self, db):
        from app.services.auth_service import login
        result = login("ghost@example.com", "any-password")
        assert result is None
