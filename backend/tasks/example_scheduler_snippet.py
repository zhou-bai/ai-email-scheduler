from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging
import re

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logging.disable(logging.CRITICAL)
for _name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.pool"):
    _l = logging.getLogger(_name)
    _l.setLevel(logging.CRITICAL)
    _l.propagate = False
    _l.handlers.clear()

from app.core.database import SessionLocal
from app.db import get_user
from app.services import calendar, gmail
from LLM import analyze_email


def main():
    db = SessionLocal()
    try:
        user_key = "kurasa907@gmail.com"
        user = get_user(db, user_key)
        if not user:
            print("No user found")
            return
        messages = gmail.fetch_emails(db, user_key, max_results=10)
        if not messages:
            print("No unread emails")
            return
        for m in messages:
            content = gmail.get_email(db, user_key, m["id"])
            subject_line = content.get("subject") or "(no subject)"
            result = analyze_email(
                content.get("body_text", ""),
                sender=content.get("from"),
                subject=content.get("subject"),
            )
            if not result or not result.get("success"):
                print(f"{subject_line} - not added")
                continue
            data = result.get("data") or {}
            if data.get("is_spam"):
                print(f"{subject_line} - not added")
                continue
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
                attendee_emails = emails
                details = {
                    "summary": summary,
                    "description": f"From: {content.get('from')}\nSubject: {subject_line}\nSummary: {email_summary}",
                    "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end_time": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timezone": "Asia/Shanghai",
                    "location": location or None,
                    "attendees": attendee_emails,
                }
                try:
                    created = calendar.create_event(db, user_key, details)
                    url = created.get("htmlLink") or created.get("id")
                    if url:
                        print(f"{subject_line} - added: {url}")
                    else:
                        print(f"{subject_line} - added")
                except Exception as e:
                    print(f"{subject_line} - failed: {e}")
            else:
                print(f"{subject_line} - not added")
    finally:
        db.close()


if __name__ == "__main__":
    main()
