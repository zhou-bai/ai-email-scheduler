from pathlib import Path
from datetime import datetime, timedelta
import os
import logging
import re

import pytest
from dotenv import load_dotenv

# 先加载 .env，确保 DB_* 等环境变量可用
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.core.config import settings
print("DB_USER:", settings.DB_USER, "DB_PASS_SET:", bool(settings.DB_PASSWORD))

# 静默 SQLAlchemy 输出，保持打印内容干净
logging.disable(logging.CRITICAL)
for _name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.pool"):
    _l = logging.getLogger(_name)
    _l.setLevel(logging.CRITICAL)
    _l.propagate = False
    _l.handlers.clear()

from app.core.database import SessionLocal
from app.db import get_user, get_or_create_user
from app.services import gmail, calendar, oauth
from app.services.email_service import create_email, update_email, delete_email
from app.services.calendar_service import (
    create_calendar_event,
    update_calendar_event,
    delete_calendar_event,
    get_user_calendar_events,
)
from app.services import email_processor as ep
from app.schemas.email import EmailCreate
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate


@pytest.mark.run(order=1)
def test_services_end_to_end():
    try:
        db = SessionLocal()
    except Exception as e:
        print("db_session_failed:", str(e))
        return
    try:
        user_key = os.getenv("TEST_USER_EMAIL") or "kurasa907@gmail.com"
        user = get_user(db, user_key) or get_or_create_user(db, user_key)
        print("user:", getattr(user, "email", None))

        try:
            msgs = gmail.fetch_emails(db, user.email, 5)
            print("gmail.fetch_emails:", len(msgs))
            if msgs:
                msg = gmail.get_email(db, user.email, msgs[0]["id"])
                print("gmail.get_email:", msg.get("subject"))
        except Exception as e:
            print("gmail_failed:", str(e))

        try:
            processed, created, message = ep.process_unread_emails(db, user.id, 5)
            print("email_processor.process_unread_emails:", processed, created, message)
        except Exception as e:
            print("email_processor_failed:", str(e))

        try:
            events = get_user_calendar_events(db, user.id, limit=5)
            print("local_events_count:", len(events))
            for ev in events:
                details = {
                    "summary": ev.summary,
                    "location": ev.location,
                    "description": ev.description,
                    "start_time": ev.start_time.isoformat(),
                    "end_time": ev.end_time.isoformat(),
                    "attendees": ev.attendees,
                    "timezone": "Asia/Shanghai",
                }
                try:
                    created_ev = calendar.create_event(db, user.email, details)
                    print("google_event_id:", created_ev.get("id"))
                    print("google_event_link:", created_ev.get("htmlLink"))
                    print("google_event_summary:", created_ev.get("summary"))
                except Exception as ce:
                    print("calendar_create_failed:", str(ce))
        except Exception as e:
            print("list_local_events_failed:", str(e))
    finally:
        try:
            db.close()
        except Exception:
            pass