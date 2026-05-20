from tests.conftest import auth


class TestAuditLogList:
    """GET /api/audit-logs/"""

    def test_returns_list(self, client, admin_token):
        res = client.get("/api/audit-logs/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_super_user_can_list(self, client, super_token):
        res = client.get("/api/audit-logs/", headers=auth(super_token))
        assert res.status_code == 200

    def test_requires_auth(self, client):
        res = client.get("/api/audit-logs/")
        assert res.status_code == 401


class TestAuditLogCreate:
    """POST /api/audit-logs/"""

    def test_creates_successfully(self, client, super_token):
        payload = {"action": "CREATE", "entity_type": "Client"}
        res = client.post("/api/audit-logs/", json=payload, headers=auth(super_token))
        assert res.status_code == 201
        data = res.get_json()
        assert data["action"] == "CREATE"
        assert data["entity_type"] == "Client"
        assert "id" in data

    def test_missing_action_returns_400(self, client, super_token):
        res = client.post("/api/audit-logs/", json={"entity_type": "Client"}, headers=auth(super_token))
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_missing_entity_type_returns_400(self, client, super_token):
        res = client.post("/api/audit-logs/", json={"action": "CREATE"}, headers=auth(super_token))
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_empty_body_returns_400(self, client, super_token):
        res = client.post("/api/audit-logs/", json={}, headers=auth(super_token))
        assert res.status_code == 400

    def test_admin_cannot_create(self, client, admin_token):
        payload = {"action": "CREATE", "entity_type": "Client"}
        res = client.post("/api/audit-logs/", json=payload, headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.post("/api/audit-logs/", json={"action": "X", "entity_type": "Y"})
        assert res.status_code == 401


class TestAuditLogGet:
    """GET /api/audit-logs/<id>"""

    def test_returns_audit_log(self, client, admin_token, audit_log_fixture):
        res = client.get(f"/api/audit-logs/{audit_log_fixture.id}", headers=auth(admin_token))
        assert res.status_code == 200
        data = res.get_json()
        assert data["id"] == str(audit_log_fixture.id)
        assert data["action"] == audit_log_fixture.action

    def test_super_user_can_get(self, client, super_token, audit_log_fixture):
        res = client.get(f"/api/audit-logs/{audit_log_fixture.id}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, admin_token):
        res = client.get("/api/audit-logs/00000000-0000-0000-0000-000000000000", headers=auth(admin_token))
        assert res.status_code == 404

    def test_requires_auth(self, client, audit_log_fixture):
        res = client.get(f"/api/audit-logs/{audit_log_fixture.id}")
        assert res.status_code == 401


class TestAuditLogUpdate:
    """PUT /api/audit-logs/<id>"""

    def test_updates_action(self, client, super_token, audit_log_fixture):
        res = client.put(
            f"/api/audit-logs/{audit_log_fixture.id}",
            json={"action": "UPDATED_ACTION"},
            headers=auth(super_token),
        )
        assert res.status_code == 200
        assert res.get_json()["action"] == "UPDATED_ACTION"

    def test_updates_entity_type(self, client, super_token, audit_log_fixture):
        res = client.put(
            f"/api/audit-logs/{audit_log_fixture.id}",
            json={"entity_type": "LoanApplication"},
            headers=auth(super_token),
        )
        assert res.status_code == 200
        assert res.get_json()["entity_type"] == "LoanApplication"

    def test_empty_body_returns_200(self, client, super_token, audit_log_fixture):
        res = client.put(
            f"/api/audit-logs/{audit_log_fixture.id}",
            json={},
            headers=auth(super_token),
        )
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.put(
            "/api/audit-logs/00000000-0000-0000-0000-000000000000",
            json={"action": "X"},
            headers=auth(super_token),
        )
        assert res.status_code == 404

    def test_admin_cannot_update(self, client, admin_token, audit_log_fixture):
        res = client.put(
            f"/api/audit-logs/{audit_log_fixture.id}",
            json={"action": "X"},
            headers=auth(admin_token),
        )
        assert res.status_code == 403

    def test_requires_auth(self, client, audit_log_fixture):
        res = client.put(f"/api/audit-logs/{audit_log_fixture.id}", json={})
        assert res.status_code == 401


class TestAuditLogDelete:
    """DELETE /api/audit-logs/<id>"""

    def test_deletes_successfully(self, client, super_token, app, db):
        from app.models.audit_log import AuditLog
        with app.app_context():
            log = AuditLog(action="to_delete", entity_type="User")
            db.session.add(log)
            db.session.commit()
            log_id = log.id

        res = client.delete(f"/api/audit-logs/{log_id}", headers=auth(super_token))
        assert res.status_code == 200
        assert "message" in res.get_json()

    def test_deleted_record_not_found(self, client, super_token, app, db):
        from app.models.audit_log import AuditLog
        with app.app_context():
            log = AuditLog(action="to_delete2", entity_type="User")
            db.session.add(log)
            db.session.commit()
            log_id = log.id

        client.delete(f"/api/audit-logs/{log_id}", headers=auth(super_token))
        res = client.get(f"/api/audit-logs/{log_id}", headers=auth(super_token))
        assert res.status_code == 404

    def test_not_found(self, client, super_token):
        res = client.delete(
            "/api/audit-logs/00000000-0000-0000-0000-000000000000",
            headers=auth(super_token),
        )
        assert res.status_code == 404

    def test_admin_cannot_delete(self, client, admin_token, audit_log_fixture):
        res = client.delete(f"/api/audit-logs/{audit_log_fixture.id}", headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client, audit_log_fixture):
        res = client.delete(f"/api/audit-logs/{audit_log_fixture.id}")
        assert res.status_code == 401
