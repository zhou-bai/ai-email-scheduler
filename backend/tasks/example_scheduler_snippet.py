from datetime import timedelta

from app.core.database import SessionLocal
from app.db import get_user
from app.services import calendar, gmail
from LLM import analyze_email

db = SessionLocal()

try:
    user_key = "kurasa907@gmail.com"

    user = get_user(db, user_key)
    if not user:
        print("No user found")
    else:
        messages = gmail.fetch_emails(db, user_key, max_results=10)
        if not messages:
            print("No unread emails")

        for m in messages:
            content = gmail.get_email(db, user_key, m["id"])
            is_spam, judge_reason, is_schedule, event, start_dt, end_dt = analyze_email(
                content.get("body_text", ""),
                sender=content.get("from"),
                subject=content.get("subject"),
            )

            if is_spam:
                print(f"Skip spam: {content.get('subject')}")
                continue

            print(f"Email: {judge_reason}")

            if is_schedule and start_dt:
                start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
                end_dt = end_dt or (start_dt + timedelta(hours=1))
                end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

                summary = event or content.get("subject") or "Auto event"
                details = {
                    "summary": summary,
                    "description": (
                        f"From email\n"
                        f"From: {content.get('from')}\n"
                        f"Subject: {content.get('subject')}\n"
                        f"Summary: {judge_reason}"
                    ),
                    "start_time": start_str,
                    "end_time": end_str,
                    "timezone": "Asia/Shanghai",
                    "attendees": [],
                }
                try:
                    created = calendar.create_event(db, user_key, details)
                    print(f"Created: {summary} -> {created.get('htmlLink')}")
                except Exception as e:
                    print(f"Failed: {e}")
            else:
                print("No event")
finally:
    db.close()
