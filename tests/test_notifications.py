from tests.conftest import auth


class TestNotificationList:
    def test_returns_list(self, client, admin_token):
        res = client.get("/api/notifications/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_requires_auth(self, client):
        res = client.get("/api/notifications/")
        assert res.status_code == 401


class TestNotificationCreate:
    VALID = {"channel": "email", "recipient": "r@r.com", "message_body": "Hello"}

    def test_creates_successfully(self, client, super_token):
        res = client.post("/api/notifications/", json=self.VALID, headers=auth(super_token))
        assert res.status_code == 201
        data = res.get_json()
        assert data["channel"] == "email"
        assert data["recipient"] == "r@r.com"

    def test_missing_channel_returns_400(self, client, super_token):
        res = client.post("/api/notifications/",
                          json={"recipient": "r@r.com", "message_body": "Hi"},
                          headers=auth(super_token))
        assert res.status_code == 400

    def test_missing_message_body_returns_400(self, client, super_token):
        res = client.post("/api/notifications/",
                          json={"channel": "sms", "recipient": "r@r.com"},
                          headers=auth(super_token))
        assert res.status_code == 400

    def test_admin_cannot_create(self, client, admin_token):
        res = client.post("/api/notifications/", json=self.VALID, headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.post("/api/notifications/", json=self.VALID)
        assert res.status_code == 401


class TestNotificationGet:
    def test_returns_notification(self, client, admin_token, notification_fixture):
        res = client.get(f"/api/notifications/{notification_fixture.id}",
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.get_json()["id"] == str(notification_fixture.id)

    def test_not_found(self, client, admin_token):
        res = client.get("/api/notifications/00000000-0000-0000-0000-000000000000",
                         headers=auth(admin_token))
        assert res.status_code == 404


class TestNotificationUpdate:
    def test_updates_status(self, client, super_token, notification_fixture):
        res = client.put(f"/api/notifications/{notification_fixture.id}",
                         json={"status": "sent"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["status"] == "sent"

    def test_updates_recipient(self, client, super_token, notification_fixture):
        res = client.put(f"/api/notifications/{notification_fixture.id}",
                         json={"recipient": "new@example.com"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["recipient"] == "new@example.com"

    def test_not_found(self, client, super_token):
        res = client.put("/api/notifications/00000000-0000-0000-0000-000000000000",
                         json={}, headers=auth(super_token))
        assert res.status_code == 404

    def test_admin_cannot_update(self, client, admin_token, notification_fixture):
        res = client.put(f"/api/notifications/{notification_fixture.id}",
                         json={}, headers=auth(admin_token))
        assert res.status_code == 403


class TestNotificationDelete:
    def test_deletes_successfully(self, client, super_token, db, loan_app_fixture):
        from app.models.notification import Notification
        n = Notification(application_id=loan_app_fixture.id,
                         channel="sms", recipient="del@del.com", message_body="bye")
        db.session.add(n)
        db.session.commit()
        nid = n.id
        res = client.delete(f"/api/notifications/{nid}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.delete("/api/notifications/00000000-0000-0000-0000-000000000000",
                            headers=auth(super_token))
        assert res.status_code == 404
