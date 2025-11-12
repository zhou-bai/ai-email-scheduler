from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.oauth import get_fresh_token


def create_event(db: Session, user_id: str, event_details: Dict[str, Any]) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("calendar", "v3", credentials=creds)
    timezone = event_details.get("timezone", "Asia/Shanghai")
    body = {
        "summary": event_details["summary"],
        "location": event_details.get("location"),
        "description": event_details.get("description"),
        "start": {"dateTime": event_details["start_time"], "timeZone": timezone},
        "end": {"dateTime": event_details["end_time"], "timeZone": timezone},
        "attendees": [{"email": e} for e in event_details.get("attendees", [])],
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
