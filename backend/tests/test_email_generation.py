#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import json
import os
import uuid
import pytest
import unittest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.email_recipient import EmailRecipient
from app.services import gmail
from app.db.helpers import get_or_create_user, get_latest_token
from app.services.email_generation import email_generation_service

def _make_client():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main as main  # type: ignore
    return TestClient(main.app)

def _ensure_user_token_and_recipient():
    db = SessionLocal()
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user = User(email=email, hashed_password="x", full_name="Test", is_active=True, role="user")
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

def _ensure_recipient(client, headers, email, name):
    r = client.post("/api/v1/recipients/", headers=headers, json={"name": name, "email": email})
    if r.status_code == 200:
        return r.json().get("id")
    lst = client.get("/api/v1/recipients/", headers=headers, params={"search": email})
    items = (lst.json() if lst.status_code == 200 else {}).get("items") or []
    rid = None
    for it in items:
        if it.get("email") == email:
            rid = it.get("id")
            break
    assert rid is not None
    return rid

def _run_create_recipient():
    client = _make_client()
    headers, recipient_id = _ensure_user_token_and_recipient()
    assert isinstance(recipient_id, int)

def _run_list_recipients():
    client = _make_client()
    headers, _ = _ensure_user_token_and_recipient()
    r = client.get("/api/v1/recipients/", headers=headers)
    print("list_recipients", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("items", []), list)

def _run_generate_and_send_email():
    client = _make_client()
    db = SessionLocal()
    user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
    user = get_or_create_user(db, user_email)
    token = get_latest_token(db, user.id)
    if not token:
        db.close()
        pytest.skip("缺少OAuth令牌，请先完成Google绑定")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})}"}
    recipient_id = _ensure_recipient(client, headers, "lovesakura2002@163.com", "收件人A")
    payload = {
        "recipient_id": recipient_id,
        "brief_content": "邀请参加下周的项目讨论会议，讨论产品规划和时间安排",
        "tone": "professional",
        "purpose": "会议邀请",
        "additional_context": "需要准备进度报告"
    }
    r1 = client.post("/api/v1/emails/generate", headers=headers, json=payload)
    print("generate", r1.status_code, r1.text)
    assert r1.status_code == 200
    gen_body = r1.json()
    assert gen_body.get("success") is True
    send_payload = {
        "recipient_id": recipient_id,
        "subject": (gen_body.get("subject") or "会议邀请") + "(已审阅)",
        "body": (gen_body.get("body") or "") + "\n请提前准备相关材料。",
        "body_html": gen_body.get("body_html")
    }
    r2 = client.post("/api/v1/emails/send", headers=headers, json=send_payload)
    print("send", r2.status_code, r2.text)
    assert r2.status_code == 200
    send_body = r2.json()
    assert send_body.get("success") is True
    assert send_body.get("gmail_message_id")
    assert send_body.get("thread_id")
    db.close()

def _run_generate_and_send_email_multiple():
    client = _make_client()
    db = SessionLocal()
    user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
    user = get_or_create_user(db, user_email)
    token = get_latest_token(db, user.id)
    if not token:
        db.close()
        pytest.skip("缺少OAuth令牌，请先完成Google绑定")
    auth_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})}"}
    rid2 = _ensure_recipient(client, auth_headers, "lovesakura2002@163.com", "收件人A")
    rid3 = _ensure_recipient(client, auth_headers, "hjq20021029@163.com", "收件人B")
    payload = {
        "recipient_ids": [rid2, rid3],
        "brief_content": "明天下午四点在102研讨室开一个代码评审会议",
        "tone": "professional",
        "purpose": "会议邀请",
        "additional_context": "需要准备进度报告"
    }
    r1 = client.post("/api/v1/emails/generate", headers=auth_headers, json=payload)
    print("generate_multi", r1.status_code, r1.text)
    assert r1.status_code == 200
    gen_body = r1.json()
    assert gen_body.get("success") is True
    send_payload = {
        "recipient_ids": [rid2, rid3],
        "subject": (gen_body.get("subject") or "会议邀请") + "(多人)",
        "body": (gen_body.get("body") or "") + "\n请确认能否出席。",
        "body_html": gen_body.get("body_html")
    }
    r2 = client.post("/api/v1/emails/send", headers=auth_headers, json=send_payload)
    print("send_multi", r2.status_code, r2.text)
    assert r2.status_code == 200
    send_body = r2.json()
    assert send_body.get("success") is True
    assert send_body.get("gmail_message_id")
    assert send_body.get("thread_id")
    db.close()

def _suite(name):
    s = unittest.TestSuite()
    s.addTest(TestEmailGeneration(name))
    return s

def test_create_recipient():
    return _suite('test_create_recipient')

def test_list_recipients():
    return _suite('test_list_recipients')

def test_generate_and_send_email():
    return _suite('test_generate_and_send_email')

def test_generate_and_send_email_multiple():
    return _suite('test_generate_and_send_email_multiple')

def test_send_real_email():
    db = SessionLocal()
    user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
    user = get_or_create_user(db, user_email)
    token = get_latest_token(db, user.id)
    if not token:
        db.close()
        pytest.skip("缺少OAuth令牌，请先完成Google绑定")
    gen = email_generation_service.generate_email_from_draft(
        subject="邀请参加讨论",
        brief_content="邀请sakura参加11.23早上10:00-11:00的讨论，关于小组作业。地点在香港大学图书馆",
        tone="professional",
        recipient_name="s4kura",
        sender_name=user.email
    )
    subject = (gen.get("data") or {}).get("subject")
    body = (gen.get("data") or {}).get("body")
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


import unittest


class TestEmailGeneration(unittest.TestCase):
    def test_generate_and_send_email_multiple(self):
        _run_generate_and_send_email_multiple()

    def test_generate_and_send_email(self):
        _run_generate_and_send_email()

    def test_list_recipients(self):
        _run_list_recipients()

    def test_create_recipient(self):
        _run_create_recipient()