from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import gmail

router = APIRouter(tags=["gmail"])


@router.get("/new")
def api_gmail_new(user_id: str, max_results: int = 10, db: Session = Depends(get_db)):
    try:
        return {"messages": gmail.fetch_emails(db, user_id, max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_id}")
def api_gmail_get(user_id: str, message_id: str, db: Session = Depends(get_db)):
    try:
        return gmail.get_email(db, user_id, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/reply")
def api_gmail_reply(
    user_id: str, message_id: str, content: str, db: Session = Depends(get_db)
):
    try:
        return gmail.reply_email(db, user_id, message_id, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
