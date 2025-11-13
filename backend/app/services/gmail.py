from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any, Dict, List
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.oauth import get_fresh_token


def fetch_emails(
    db: Session, user_id: str, max_results: int = 10
) -> List[Dict[str, Any]]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    result = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results)
        .execute()
    )
    return result.get("messages", [])


def get_email(db: Session, user_id: str, email_id: str) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=email_id, format="full")
        .execute()
    )

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body_text = _extract_body(msg.get("payload", {}))

    return {
        "id": email_id,
        "threadId": msg.get("threadId"),
        "snippet": msg.get("snippet"),
        "from": headers.get("From"),
        "to": headers.get("To"),
        "subject": headers.get("Subject"),
        "date": headers.get("Date"),
        "body_text": body_text,
    }


def reply_email(
    db: Session, user_id: str, email_id: str, content: str
) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    original = (
        service.users()
        .messages()
        .get(userId="me", id=email_id, format="full")
        .execute()
    )

    headers = {
        h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])
    }
    to_addr = headers.get("From")
    subject = headers.get("Subject", "(no subject)")
    message_id = headers.get("Message-Id") or headers.get("Message-ID")

    mime_msg = email.message.EmailMessage()
    mime_msg["To"] = to_addr
    mime_msg["Subject"] = f"Re: {subject}"
    if message_id:
        mime_msg["In-Reply-To"] = message_id
        mime_msg["References"] = message_id
    mime_msg.set_content(content)

    raw = urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    return (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw, "threadId": original.get("threadId")})
        .execute()
    )


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


def _extract_body(payload: Dict[str, Any]) -> str:
    d = payload.get("body", {}).get("data")
    if d:
        return urlsafe_b64decode(d.encode("utf-8")).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            d = part.get("body", {}).get("data")
            if d:
                return urlsafe_b64decode(d.encode("utf-8")).decode(
                    "utf-8", errors="ignore"
                )
    return ""
