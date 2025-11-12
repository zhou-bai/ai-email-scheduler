from typing import List, Dict, Any
from base64 import urlsafe_b64decode, urlsafe_b64encode
import email

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.core.config import settings
from app.infrastructure.token_store import TokenStore


def _get_credentials(user_id: str, store: TokenStore) -> Credentials:
    tokens = store.get_tokens(user_id)
    if not tokens:
        raise RuntimeError("No tokens found for user.")
    creds = Credentials(
        tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_uri=settings.GOOGLE_TOKEN_URI,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GOOGLE_SCOPES,
    )
    if not creds.valid or creds.expired:
        creds.refresh(Request())
        store.update_tokens(user_id, access_token=creds.token, expiry=creds.expiry)
    return creds


def fetch_new_emails(
    user_id: str, store: TokenStore, max_results: int = 10
) -> List[Dict[str, Any]]:
    creds = _get_credentials(user_id, store)
    service = build("gmail", "v1", credentials=creds)
    result = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results)
        .execute()
    )
    return result.get("messages", [])


def get_email_content(user_id: str, store: TokenStore, email_id: str) -> Dict[str, Any]:
    creds = _get_credentials(user_id, store)
    service = build("gmail", "v1", credentials=creds)
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=email_id, format="full")
        .execute()
    )

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body_text = _extract_body_text(msg.get("payload", {}))
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


def _extract_body_text(payload: Dict[str, Any]) -> str:
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


def send_reply(
    user_id: str, store: TokenStore, email_id: str, content: str
) -> Dict[str, Any]:
    creds = _get_credentials(user_id, store)
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
