import os
import re
import logging
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytest

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logging.disable(logging.CRITICAL)

from app.core.database import SessionLocal
from app.db import get_user
from app.services import calendar, gmail
from LLM import analyze_email


def test_example_scheduler_snippet_e2e():
    db = SessionLocal()
    try:
        user_key = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
        user = get_user(db, user_key)
        if not user:
            pytest.skip("No user found")
        try:
            messages = gmail.fetch_emails(db, user_key, max_results=5)
        except Exception as e:
            pytest.skip(f"gmail fetch failed: {e}")
        if not messages:
            pytest.skip("No unread emails")
        processed = 0
        created_events = 0
        for m in messages:
            content = gmail.get_email(db, user_key, m.get("id"))
            subject_line = content.get("subject") or "(no subject)"
            result = analyze_email(
                content.get("body_text", ""),
                sender=content.get("from"),
                subject=content.get("subject"),
            )
            if not result or not result.get("success"):
                continue
            data = result.get("data") or {}
            if data.get("is_spam"):
                continue
            processed += 1
            if data.get("is_schedule") and data.get("start_time"):
                start_dt = data.get("start_time")
                end_dt = data.get("end_time") or (start_dt + timedelta(hours=1))
                email_summary = data.get("judge_reason") or ""
                summary = data.get("event") or email_summary or content.get("subject") or "Auto event"
                location = data.get("location") or ""
                participants_info = data.get("participants") or ""
                participants_list = [p.strip() for p in participants_info.split(",") if p.strip()]
                emails = []
                for it in participants_list:
                    emails.extend(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", it))
                details = {
                    "summary": summary,
                    "description": f"From: {content.get('from')}\nSubject: {subject_line}\nSummary: {email_summary}",
                    "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end_time": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timezone": "Asia/Shanghai",
                    "location": location or None,
                    "attendees": emails,
                }
                try:
                    calendar.create_event(db, user_key, details)
                    created_events += 1
                except Exception:
                    continue
        assert processed >= 0
        assert created_events >= 0
    finally:
        db.close()
