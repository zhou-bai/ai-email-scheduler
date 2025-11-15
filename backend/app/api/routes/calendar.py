from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services import calendar

router = APIRouter(tags=["calendar"])


@router.post("/events")
def api_calendar_create(
    summary: str,
    start_time: str,
    end_time: str,
    timezone: str = "Asia/Shanghai",
    location: str | None = None,
    attendees: str | None = None,
    description: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        body = {
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "timezone": timezone,
            "location": location,
            "attendees": attendees,
            "description": description,
        }
        return calendar.create_event(db, str(current_user.id), body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
