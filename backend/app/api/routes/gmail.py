from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services import gmail

router = APIRouter(tags=["gmail"])


@router.get("/new")
def api_gmail_new(
    max_results: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return {"messages": gmail.fetch_emails(db, str(current_user.id), max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_id}")
def api_gmail_get(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return gmail.get_email(db, str(current_user.id), message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/reply")
def api_gmail_reply(
    message_id: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return gmail.reply_email(db, str(current_user.id), message_id, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
