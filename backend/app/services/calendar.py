from typing import Any, Dict, List
import re

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.oauth import get_fresh_token


def create_event(db: Session, user_id: str, event_details: Dict[str, Any]) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("calendar", "v3", credentials=creds)
    timezone = event_details.get("timezone", "Asia/Shanghai")
    attendees = _normalize_attendees(event_details.get("attendees"))
    body = {
        "summary": event_details["summary"],
        "location": event_details.get("location"),
        "description": event_details.get("description"),
        "start": {"dateTime": event_details["start_time"], "timeZone": timezone},
        "end": {"dateTime": event_details["end_time"], "timeZone": timezone},
        "attendees": attendees,
    }
    return service.events().insert(calendarId="primary", body=body).execute()


def find_free_slots(
    db: Session,
    user_id: str,
    time_min: str,
    time_max: str,
    calendars: List[str] = None,
) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("calendar", "v3", credentials=creds)
    items = [{"id": "primary"}] if not calendars else [{"id": c} for c in calendars]
    body = {"timeMin": time_min, "timeMax": time_max, "items": items}
    return service.freebusy().query(body=body).execute()


def _get_creds(db: Session, user_id: str) -> Credentials:
    access_token = get_fresh_token(db, user_id)
    creds = Credentials(
        access_token,
        token_uri=settings.GOOGLE_TOKEN_URI,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GOOGLE_SCOPES,
    )
    return creds


def _normalize_attendees(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [x.strip() for x in value.split(",") if x.strip()]
        emails: List[str] = []
        for it in items:
            emails.extend(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", it))
        return [{"email": e} for e in emails]
    if isinstance(value, list):
        if all(isinstance(x, dict) and "email" in x for x in value):
            return [{"email": x["email"]} for x in value if re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", x.get("email", ""))]
        items = [str(x).strip() for x in value if str(x).strip()]
        emails: List[str] = []
        for s in items:
            emails.extend(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", s))
        return [{"email": e} for e in emails]
    return []
