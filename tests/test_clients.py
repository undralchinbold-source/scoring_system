from tests.conftest import auth


class TestClientList:
    def test_returns_list(self, client, admin_token):
        res = client.get("/api/clients/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_requires_auth(self, client):
        res = client.get("/api/clients/")
        assert res.status_code == 401


class TestClientCreate:
    def test_creates_successfully(self, client, super_token):
        res = client.post("/api/clients/", json={
            "national_id": "BB11111111",
            "fullname": "New Client",
        }, headers=auth(super_token))
        assert res.status_code == 201
        assert res.get_json()["national_id"] == "BB11111111"

    def test_missing_national_id_returns_400(self, client, super_token):
        res = client.post("/api/clients/", json={"fullname": "X"}, headers=auth(super_token))
        assert res.status_code == 400

    def test_missing_fullname_returns_400(self, client, super_token):
        res = client.post("/api/clients/", json={"national_id": "CC22222222"}, headers=auth(super_token))
        assert res.status_code == 400

    def test_duplicate_national_id_returns_409(self, client, super_token, client_fixture):
        res = client.post("/api/clients/", json={
            "national_id": client_fixture.national_id,
            "fullname": "Duplicate",
        }, headers=auth(super_token))
        assert res.status_code == 409

    def test_admin_cannot_create(self, client, admin_token):
        res = client.post("/api/clients/", json={
            "national_id": "DD33333333", "fullname": "X",
        }, headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.post("/api/clients/", json={"national_id": "X", "fullname": "X"})
        assert res.status_code == 401


class TestClientGet:
    def test_returns_client(self, client, admin_token, client_fixture):
        res = client.get(f"/api/clients/{client_fixture.id}", headers=auth(admin_token))
        assert res.status_code == 200
        assert res.get_json()["id"] == str(client_fixture.id)

    def test_not_found(self, client, admin_token):
        res = client.get("/api/clients/00000000-0000-0000-0000-000000000000", headers=auth(admin_token))
        assert res.status_code == 404

    def test_requires_auth(self, client, client_fixture):
        res = client.get(f"/api/clients/{client_fixture.id}")
        assert res.status_code == 401


class TestClientUpdate:
    def test_updates_fullname(self, client, super_token, client_fixture):
        res = client.put(f"/api/clients/{client_fixture.id}",
                         json={"fullname": "Updated Name"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["fullname"] == "Updated Name"

    def test_updates_phone(self, client, super_token, client_fixture):
        res = client.put(f"/api/clients/{client_fixture.id}",
                         json={"phone": "99991234"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["phone"] == "99991234"

    def test_not_found(self, client, super_token):
        res = client.put("/api/clients/00000000-0000-0000-0000-000000000000",
                         json={}, headers=auth(super_token))
        assert res.status_code == 404

    def test_admin_cannot_update(self, client, admin_token, client_fixture):
        res = client.put(f"/api/clients/{client_fixture.id}",
                         json={"fullname": "X"}, headers=auth(admin_token))
        assert res.status_code == 403


class TestClientDelete:
    def test_deletes_successfully(self, client, super_token, db):
        from app.models.client import Client
        c = Client(national_id="ZZ99999999", fullname="To Delete")
        db.session.add(c)
        db.session.commit()
        cid = c.id
        res = client.delete(f"/api/clients/{cid}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.delete("/api/clients/00000000-0000-0000-0000-000000000000",
                            headers=auth(super_token))
        assert res.status_code == 404

    def test_admin_cannot_delete(self, client, admin_token, client_fixture):
        res = client.delete(f"/api/clients/{client_fixture.id}", headers=auth(admin_token))
        assert res.status_code == 403
