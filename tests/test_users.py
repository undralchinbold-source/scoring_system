from tests.conftest import auth


class TestUserList:
    def test_returns_list(self, client, admin_token):
        res = client.get("/api/users/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_requires_auth(self, client):
        res = client.get("/api/users/")
        assert res.status_code == 401


class TestUserCreate:
    VALID = {"email": "new@example.com", "password": "pass123", "role": "admin", "fullname": "New User"}

    def test_creates_successfully(self, client, super_token):
        res = client.post("/api/users/", json=self.VALID, headers=auth(super_token))
        assert res.status_code == 201
        data = res.get_json()
        assert data["email"] == "new@example.com"
        assert "password_hash" not in data

    def test_missing_fields_returns_400(self, client, super_token):
        res = client.post("/api/users/", json={"email": "x@x.com"}, headers=auth(super_token))
        assert res.status_code == 400

    def test_duplicate_email_returns_409(self, client, super_token, user_fixture):
        res = client.post("/api/users/", json={
            "email": user_fixture.email, "password": "p", "role": "admin", "fullname": "X",
        }, headers=auth(super_token))
        assert res.status_code == 409

    def test_invalid_role_returns_400(self, client, super_token):
        res = client.post("/api/users/", json={
            "email": "r@r.com", "password": "p", "role": "manager", "fullname": "X",
        }, headers=auth(super_token))
        assert res.status_code == 400

    def test_admin_cannot_create(self, client, admin_token):
        res = client.post("/api/users/", json=self.VALID, headers=auth(admin_token))
        assert res.status_code == 403


class TestUserGet:
    def test_returns_user(self, client, admin_token, user_fixture):
        res = client.get(f"/api/users/{user_fixture.id}", headers=auth(admin_token))
        assert res.status_code == 200
        assert res.get_json()["email"] == user_fixture.email

    def test_not_found(self, client, admin_token):
        res = client.get("/api/users/00000000-0000-0000-0000-000000000000", headers=auth(admin_token))
        assert res.status_code == 404


class TestUserUpdate:
    def test_updates_fullname(self, client, super_token, user_fixture):
        res = client.put(f"/api/users/{user_fixture.id}",
                         json={"fullname": "Updated"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["fullname"] == "Updated"

    def test_invalid_role_returns_400(self, client, super_token, user_fixture):
        res = client.put(f"/api/users/{user_fixture.id}",
                         json={"role": "hacker"}, headers=auth(super_token))
        assert res.status_code == 400

    def test_valid_role_update(self, client, super_token, user_fixture):
        res = client.put(f"/api/users/{user_fixture.id}",
                         json={"role": "super_user"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["role"] == "super_user"

    def test_not_found(self, client, super_token):
        res = client.put("/api/users/00000000-0000-0000-0000-000000000000",
                         json={}, headers=auth(super_token))
        assert res.status_code == 404


class TestUserDelete:
    def test_deletes_successfully(self, client, super_token, db):
        from werkzeug.security import generate_password_hash
        from app.models.user import User
        u = User(email="del@del.com", password_hash=generate_password_hash("x"),
                 role="admin", fullname="Del")
        db.session.add(u)
        db.session.commit()
        uid = u.id
        res = client.delete(f"/api/users/{uid}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.delete("/api/users/00000000-0000-0000-0000-000000000000",
                            headers=auth(super_token))
        assert res.status_code == 404
