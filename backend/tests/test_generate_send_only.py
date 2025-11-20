#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import os
import warnings
import uuid
import pytest
import unittest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.db.helpers import get_or_create_user, get_latest_token


def _make_client():
    import main as main  # type: ignore
    return TestClient(main.app)


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


def _run_generate_only():
    client = _make_client()
    db = SessionLocal()
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user = get_or_create_user(db, email)
    token = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    rid = _ensure_recipient(client, headers, f"rcpt-{uuid.uuid4().hex[:8]}@example.com", "测试收件人")
    payload = {
        "recipient_id": rid,
        "brief_content": "邀请参加下周的项目讨论会议，讨论产品规划和时间安排",
        "tone": "professional",
        "purpose": "会议邀请",
        "additional_context": "需要准备进度报告"
    }
    r = client.post("/api/v1/emails/generate", headers=headers, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert (body.get("subject") or "").strip() != ""
    assert (body.get("body") or "").strip() != ""
    print(f"用户输入的内容：{payload['brief_content']}")
    print("AI生成的内容：")
    print(f"主题：{body.get('subject')}")
    print(f"正文：{body.get('body')}")


def _run_generate_only_with_identity():
    client = _make_client()
    db = SessionLocal()
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user = get_or_create_user(db, email)
    token = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    rid = _ensure_recipient(client, headers, f"rcpt-{uuid.uuid4().hex[:8]}@example.com", "测试收件人")
    payload = {
        "recipient_id": rid,
        "brief_content": "邀请参加下周的项目讨论会议，讨论产品规划和时间安排",
        "tone": "professional",
        "purpose": "会议邀请",
        "additional_context": "需要准备进度报告",
        "sender_name": "张三",
        "sender_position": "项目经理",
        "sender_contact": "电话: 123-456-7890"
    }
    r = client.post("/api/v1/emails/generate", headers=headers, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert (body.get("subject") or "").strip() != ""
    assert (body.get("body") or "").strip() != ""
    print(f"用户输入的内容：{payload['brief_content']}")
    print("AI生成的内容（包含身份信息）：")
    print(f"主题：{body.get('subject')}")
    print(f"正文：{body.get('body')}")


def _run_send_only():
    client = _make_client()
    db = SessionLocal()
    user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
    user = get_or_create_user(db, user_email)
    token = get_latest_token(db, user.id)
    if not token:
        db.close()
        pytest.skip("缺少OAuth令牌，请先完成Google绑定")
    auth = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth}"}
    rid = _ensure_recipient(client, headers, "lovesakura2002@163.com", "收件人A")
    payload = {
        "recipient_id": rid,
        "subject": "仅发送测试-会议通知",
        "body": "这是一封仅发送测试邮件，用于验证发送接口",
        "body_html": None
    }
    r = client.post("/api/v1/emails/send", headers=headers, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert body.get("gmail_message_id")
    assert body.get("thread_id")
    db.close()


class TestGenerateSendOnly(unittest.TestCase):
    def test_generate_only(self):
        _run_generate_only()

    def test_send_only(self):
        _run_send_only()

    def test_generate_only_with_identity(self):
        _run_generate_only_with_identity()

    def test_generate_only_direct_email(self):
        client = _make_client()
        db = SessionLocal()
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        user = get_or_create_user(db, email)
        token = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

        payload = {
            "to_email": "someone@example.com",
            "brief_content": "邀请参加下周的项目讨论会议，讨论产品规划和时间安排",
            "tone": "professional"
        }
        r = client.post("/api/v1/emails/generate", headers=headers, json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("success") is True
        print(f"用户输入的内容：{payload['brief_content']}")
        print("AI生成的内容（直接邮箱）：")
        print(f"主题：{body.get('subject')}")
        print(f"正文：{body.get('body')}")

    def test_send_only_direct_emails(self):
        client = _make_client()
        db = SessionLocal()
        user_email = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
        user = get_or_create_user(db, user_email)
        token = get_latest_token(db, user.id)
        if not token:
            db.close()
            pytest.skip("缺少OAuth令牌，请先完成Google绑定")
        auth = create_access_token(subject=str(user.id), additional_claims={"email": user.email, "role": user.role})
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth}"}
        payload = {
            "to_emails": ["lovesakura2002@163.com", "hjq20021029@163.com"],
            "subject": "仅发送测试-多人",
            "body": "这是一封仅发送测试邮件（直接邮箱），用于验证发送接口",
            "body_html": None
        }
        r = client.post("/api/v1/emails/send", headers=headers, json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("success") is True
        assert body.get("gmail_message_id")
        assert body.get("thread_id")
        db.close()


def _suite(name):
    s = unittest.TestSuite()
    s.addTest(TestGenerateSendOnly(name))
    return s


def test_generate_only():
    return _suite('test_generate_only')


def test_send_only():
    return _suite('test_send_only')


def test_generate_only_with_identity():
    return _suite('test_generate_only_with_identity')
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*co_lnotab is deprecated.*")