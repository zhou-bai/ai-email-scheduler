from typing import Dict, Any, List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, TOKEN_URI, SCOPES
from backend.infrastructure.token_store import TokenStore

def _get_credentials(user_id: str, store: TokenStore) -> Credentials:
    tokens = store.get_tokens(user_id)
    if not tokens:
        raise RuntimeError("No tokens found for user.")
    creds = Credentials(
        tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_uri=TOKEN_URI,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    if not creds.valid or creds.expired:
        creds.refresh(Request())
        store.update_tokens(user_id, access_token=creds.token, expiry=creds.expiry)
    return creds

def create_event(user_id: str, store: TokenStore, event_details: Dict[str, Any]) -> Dict[str, Any]:
    creds = _get_credentials(user_id, store)
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

def find_free_slots(user_id: str, store: TokenStore, time_min: str, time_max: str, calendars: List[str] = None) -> Dict[str, Any]:
    creds = _get_credentials(user_id, store)
    service = build("calendar", "v3", credentials=creds)
    items = [{"id": "primary"}] if not calendars else [{"id": c} for c in calendars]
    body = {"timeMin": time_min, "timeMax": time_max, "items": items}
    return service.freebusy().query(body=body).execute()