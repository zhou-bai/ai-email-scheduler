#!/usr/bin/env python3
import json
import os
import uuid
import pytest

from app.core.database import SessionLocal
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.email_recipient import EmailRecipient
from app.services import gmail
from app.db.helpers import get_or_create_user, get_latest_token
from app.services.email_generation import email_generation_service

def _ensure_user_token_and_recipient():
    db = SessionLocal()
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user = User(email=email, hashed_password=get_password_hash("Test12345!"), full_name="Test", is_active=True, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    recipient = EmailRecipient(user_id=user.id, name="测试收件人", email=f"rcpt-{uuid.uuid4().hex[:8]}@example.com")
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    token = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
    db.close()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return headers, recipient.id

def test_create_recipient(client):
    headers, recipient_id = _ensure_user_token_and_recipient()
    assert isinstance(recipient_id, int)

def test_list_recipients(client):
    headers, _ = _ensure_user_token_and_recipient()
    r = client.get("/api/v1/recipients/", headers=headers)
    print("list_recipients", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("items", []), list)

def test_generate_and_send_email(client, monkeypatch):
    headers, recipient_id = _ensure_user_token_and_recipient()
    def fake_generate(**kwargs):
        return {"success": True, "data": {"subject": "会议邀请", "body": "内容", "body_html": "<p>内容</p>"}, "message": "ok"}
    def fake_send(**kwargs):
        return {"success": True, "message_id": "mid", "thread_id": "tid", "message": "ok"}
    monkeypatch.setattr("app.services.email_generation.email_generation_service.generate_email_from_draft", lambda **kw: fake_generate(**kw))
    monkeypatch.setattr("app.services.gmail.send_email", lambda **kw: fake_send(**kw))
    payload = {
        "recipient_id": recipient_id,
        "brief_content": "邀请参加下周的项目讨论会议，讨论产品规划和时间安排",
        "tone": "professional",
        "purpose": "会议邀请",
        "additional_context": "需要准备进度报告"
    }
    r = client.post("/api/v1/emails/generate-and-send", headers=headers, json=payload)
    print("generate_and_send", r.status_code, r.text)
    assert r.status_code == 200
    body = r.json()
    assert "success" in body

def test_send_real_email():
    db = SessionLocal()
    user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
    user = get_or_create_user(db, user_email)
    token = get_latest_token(db, user.id)
    if not token:
        db.close()
        pytest.skip("缺少OAuth令牌，请先完成Google绑定")
    gen = email_generation_service.generate_email_from_draft(
        subject=None,
        brief_content="明天下午四点在102研讨室开一个代码评审会议",
        tone="professional",
        recipient_name="s4kura",
        sender_name=user.email,
        purpose="会议邀请",
        additional_context="需要准备进度报告"
    )
    subject = (gen.get("data") or {}).get("subject") or f"测试发送 {uuid.uuid4().hex[:6]}"
    body = (gen.get("data") or {}).get("body") or "这是一封测试邮件"
    body_html = (gen.get("data") or {}).get("body_html")
    res = gmail.send_email(
        db=db,
        user_id=user_email,
        to_email="lovesakura2002@163.com",
        subject=subject,
        body=body,
        body_html=body_html
    )
    db.close()
    assert res.get("success") is True