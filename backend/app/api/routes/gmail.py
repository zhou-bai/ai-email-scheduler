from fastapi import APIRouter, HTTPException
from infrastructure.token_store import _store
from services.gmail_client import fetch_new_emails, get_email_content, send_reply

router = APIRouter(tags=["gmail"])


@router.get("/new")
def api_gmail_new(user_id: str, max_results: int = 10):
    try:
        return {"messages": fetch_new_emails(user_id, _store, max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_id}")
def api_gmail_get(user_id: str, message_id: str):
    try:
        return get_email_content(user_id, _store, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/reply")
def api_gmail_reply(user_id: str, message_id: str, content: str):
    try:
        return send_reply(user_id, _store, message_id, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
