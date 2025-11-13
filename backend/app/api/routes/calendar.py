from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import calendar

router = APIRouter(tags=["calendar"])


@router.post("/events")
def api_calendar_create(
    user_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    timezone: str = "Asia/Shanghai",
    db: Session = Depends(get_db),
):
    try:
        body = {
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "timezone": timezone,
        }
        return calendar.create_event(db, user_id, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
