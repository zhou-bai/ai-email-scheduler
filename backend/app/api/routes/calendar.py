from fastapi import APIRouter, HTTPException

from infrastructure.token_store import TokenStore
from services.calendar_client import create_event

router = APIRouter(tags=["calendar"])
store = TokenStore()


@router.post("/events")
def api_calendar_create(
    user_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    timezone: str = "Asia/Shanghai",
):
    try:
        body = {
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "timezone": timezone,
        }
        return create_event(user_id, store, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
