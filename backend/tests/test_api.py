from datetime import datetime, timedelta, UTC
import backend.main as main


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "AI Email and Scheduling Assistant - Backend API"}


def test_status(client):
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    assert resp.json() == {"status": "running"}


def test_auth_url_success(client, monkeypatch):
    def fake_build(user_id: str):
        assert user_id == "user-123"
        return "https://example.test/oauth?state=abc"

    monkeypatch.setattr(main, "build_google_auth_url", fake_build)
    resp = client.get("/api/v1/auth/google/url", params={"user_id": "user-123"})
    assert resp.status_code == 200
    assert resp.json() == {"auth_url": "https://example.test/oauth?state=abc"}


def test_auth_url_error(client, monkeypatch):
    def fake_build(user_id: str):
        raise RuntimeError("bad creds")

    monkeypatch.setattr(main, "build_google_auth_url", fake_build)
    resp = client.get("/api/v1/auth/google/url", params={"user_id": "user-123"})
    assert resp.status_code == 500
    assert "bad creds" in resp.json()["detail"]


def test_oauth_callback_success_with_user_id(client, monkeypatch):
    def fake_exchange(code: str):
        # 使用具备时区的 UTC 时间，避免弃用警告
        return "acc-token", "ref-token", datetime.now(UTC) + timedelta(hours=1)

    monkeypatch.setattr(main, "exchange_code_for_tokens", fake_exchange)

    resp = client.get(
        "/api/v1/auth/google/callback",
        params={"code": "ok-code", "user_id": "user-abc"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"success": True}

    # 验证令牌已保存到内存存储
    tokens = main.store.get_tokens("user-abc")
    assert tokens is not None
    assert tokens.access_token == "acc-token"
    assert tokens.refresh_token == "ref-token"
    assert tokens.expiry is not None


def test_oauth_callback_missing_user_id_and_state_returns_400(client, monkeypatch):
    def fake_exchange(code: str):
        # 使用具备时区的 UTC 时间，避免弃用警告
        return "acc-token", "ref-token", datetime.now(UTC) + timedelta(hours=1)

    monkeypatch.setattr(main, "exchange_code_for_tokens", fake_exchange)

    resp = client.get("/api/v1/auth/google/callback", params={"code": "ok-code"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Missing user_id/state"


def test_gmail_new_list(client, monkeypatch):
    def fake_fetch(user_id, store, max_results=10):
        assert user_id == "u1"
        assert max_results == 5
        return [{"id": "m1"}, {"id": "m2"}]

    monkeypatch.setattr(main, "fetch_new_emails", fake_fetch)

    resp = client.get("/api/v1/gmail/new", params={"user_id": "u1", "max_results": 5})
    assert resp.status_code == 200
    assert resp.json() == {"messages": [{"id": "m1"}, {"id": "m2"}]}


def test_gmail_get_content(client, monkeypatch):
    def fake_get(user_id, store, message_id):
        assert user_id == "u1"
        assert message_id == "mid-123"
        return {
            "id": "mid-123",
            "threadId": "t1",
            "snippet": "hello",
            "from": "a@example.com",
            "to": "b@example.com",
            "subject": "subj",
            "date": "2025-01-01",
            "body_text": "body",
        }

    monkeypatch.setattr(main, "get_email_content", fake_get)

    resp = client.get("/api/v1/gmail/mid-123", params={"user_id": "u1"})
    assert resp.status_code == 200
    assert resp.json()["id"] == "mid-123"
    assert resp.json()["subject"] == "subj"


def test_gmail_reply_send(client, monkeypatch):
    def fake_reply(user_id, store, message_id, content):
        assert user_id == "u1"
        assert message_id == "mid-123"
        assert content == "Thanks!"
        return {"sent": True, "to": "a@example.com"}

    monkeypatch.setattr(main, "send_reply", fake_reply)

    resp = client.post(
        "/api/v1/gmail/mid-123/reply",
        params={"user_id": "u1", "content": "Thanks!"}
    )
    assert resp.status_code == 200
    assert resp.json()["sent"] is True


def test_calendar_create_event(client, monkeypatch):
    def fake_create(user_id, store, body):
        assert user_id == "u1"
        assert body["summary"] == "Meet"
        assert body["start_time"] == "2025-01-01T10:00:00Z"
        assert body["end_time"] == "2025-01-01T11:00:00Z"
        assert body["timezone"] == "Asia/Shanghai"
        return {"id": "evt-1", "status": "confirmed"}

    monkeypatch.setattr(main, "create_event", fake_create)

    resp = client.post(
        "/api/v1/calendar/events",
        params={
            "user_id": "u1",
            "summary": "Meet",
            "start_time": "2025-01-01T10:00:00Z",
            "end_time": "2025-01-01T11:00:00Z",
            "timezone": "Asia/Shanghai",
        }
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == "evt-1"
    assert resp.json()["status"] == "confirmed"