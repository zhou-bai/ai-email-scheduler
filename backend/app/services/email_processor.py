from __future__ import annotations

from datetime import datetime, timedelta
from typing import Tuple, List
import re

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.schemas.calendar import CalendarEventCreate
from app.schemas.email import EmailCreate
from app.services import gmail
from app.services.calendar_service import create_calendar_event
from app.services.email_service import create_email, get_email_by_email_id
from LLM import analyze_email

logger = get_logger(__name__)


def process_unread_emails(
    db: Session, user_id: int, max_results: int
) -> Tuple[int, int, str]:
    messages = gmail.fetch_emails(db, str(user_id), max_results)
    if not messages:
        return 0, 0, "No new emails to process"

    processed = 0
    created_events = 0

    for msg in messages:
        email_id = msg.get("id")
        if not email_id:
            logger.warning("Skipping message with missing id")
            continue

        if get_email_by_email_id(db, str(email_id)):
            logger.info("Email %s already processed, skipping", email_id)
            continue

        email_data = gmail.get_email(db, str(user_id), email_id)
        result = analyze_email(
            email_content=email_data.get("body_text", ""),
            sender=email_data.get("from"),
            subject=email_data.get("subject"),
            recipients=email_data.get("to"),
        )

        if not result or not result.get("success"):
            logger.warning("LLM analyze failed for email %s", email_id)
            continue

        data = result.get("data") or {}
        is_spam = bool(data.get("is_spam"))
        judge_reason = data.get("judge_reason") or ""
        is_schedule = bool(data.get("is_schedule"))
        event_name = data.get("event") or None
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        location = data.get("location") or None
        participants_info = data.get("participants") or ""
        participants_list: List[str] = [p.strip() for p in participants_info.split(",") if p.strip()]
        emails: List[str] = []
        for item in participants_list:
            emails.extend(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", item))
        seen: set[str] = set()
        valid_emails = [e for e in emails if not (e in seen or seen.add(e))]
        attendee_emails = ",".join(valid_emails) or None

        if is_spam:
            logger.info(
                "Skipping spam email %s: subject='%s'",
                email_id,
                email_data.get("subject"),
            )
            continue

        received_at = None
        if email_data.get("date"):
            try:
                from email.utils import parsedate_to_datetime

                received_at = parsedate_to_datetime(email_data["date"])
            except Exception as e:  # noqa: BLE001
                logger.warning("Failed to parse date: %s", e)
                received_at = datetime.now()

        email_create = EmailCreate(
            user_id=user_id,
            email_id=email_id,
            thread_id=email_data.get("threadId"),
            from_address=email_data.get("from"),
            to_address=email_data.get("to"),
            subject=email_data.get("subject"),
            received_at=received_at,
            snippet=judge_reason[:500] if judge_reason else email_data.get("snippet"),
            body_text=email_data.get("body_text"),
        )
        create_email(db, email_create)
        processed += 1

        if is_schedule and start_time:
            if not end_time:
                end_time = start_time + timedelta(hours=1)
                logger.debug(
                    "Email %s: end_time missing, defaulted to %s",
                    email_id,
                    end_time.isoformat(),
                )

            summary = event_name or email_data.get("subject") or "Meeting"
            # insert to local calendar
            try:
                description_text = (
                    f"From: {email_data.get('from')}\n"
                    f"Subject: {email_data.get('subject')}\n"
                    f"Summary: {judge_reason}\n"
                    f"Location: {location or 'None'}\n"
                    f"Participants: {participants_info or 'None'}"
                )
                calendar_event_data = CalendarEventCreate(
                    user_id=user_id,
                    summary=summary,
                    description=description_text,
                    start_time=start_time,
                    end_time=end_time,
                    location=location,
                    attendees=attendee_emails,
                )
                db_event = create_calendar_event(db, calendar_event_data)
                created_events += 1
                logger.info(
                    "Stored local calendar event from email %s -> db_id=%s",
                    email_id,
                    db_event.id,
                )
            except Exception as ce:  # noqa: BLE001
                logger.error(
                    "Failed to store local calendar event from email %s: %s",
                    email_id,
                    ce,
                    exc_info=True,
                )
        else:
            logger.debug(
                "Email %s: no schedulable event detected (is_schedule=%s)",
                email_id,
                is_schedule,
            )

        logger.info("Processed email %s: schedule=%s", email_id, is_schedule)

    message = f"Successfully processed {processed} emails, created {created_events} calendar events"
    return processed, created_events, message
