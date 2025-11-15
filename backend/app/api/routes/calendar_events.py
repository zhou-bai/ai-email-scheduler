from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate,
    ConfirmScheduleResponse,
)
from app.services.calendar import create_event as create_google_event
from app.services.calendar_service import (
    create_calendar_event,
    delete_calendar_event,
    get_calendar_event_by_id,
    get_user_calendar_events,
    update_calendar_event,
)

router = APIRouter(tags=["calendar_events"])


@router.post(
    "/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED
)
def create_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new calendar event

    Security: Requires authentication, event is automatically associated with the current user
    """
    return create_calendar_event(db, event_data)


@router.get("/{event_id}", response_model=CalendarEventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_calendar_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
        )

    # check ownership
    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this event",
        )

    return event


@router.get("/", response_model=List[CalendarEventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all calendar events for a user"""
    return get_user_calendar_events(db, current_user.id, skip, limit)


@router.put("/{event_id}", response_model=CalendarEventResponse)
def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 先获取事件验证所有权
    event = get_calendar_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
        )

    # check ownership
    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this event",
        )

    updated_event = update_calendar_event(db, event_id, event_data)
    return updated_event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_calendar_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
        )

    # check ownership
    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this event",
        )

    # Perform deletion
    delete_calendar_event(db, event_id)
    return {"success": True, "message": "Calendar event deleted successfully"}


@router.post("/{event_id}/confirm", response_model=ConfirmScheduleResponse)
def confirm_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm an LLM-created calendar event: push to Google Calendar then delete local record.

    Flow:
    1. Fetch local event (must belong to current user)
    2. Create event in user's Google Calendar
    3. Delete local event entry
    4. Return Google event id and original (deleted) local id
    """
    event = get_calendar_event_by_id(db, event_id)
    if not event or event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
        )

    event_details = {
        "summary": event.summary,
        "location": event.location,
        "description": event.description,
        "start_time": event.start_time.isoformat(),  # RFC3339
        "end_time": event.end_time.isoformat(),
        "attendees": [
            {"email": e.strip()} for e in event.attendees.split(",") if e.strip()
        ]
        if event.attendees
        else [],
        "timezone": "Asia/Shanghai",
    }

    try:
        google_event = create_google_event(db, str(current_user.id), event_details)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create Google Calendar event: {e}",
        )

    # Delete local event after successful sync
    delete_calendar_event(db, event_id)

    return ConfirmScheduleResponse(
        success=True,
        message="Event confirmed and synced to Google Calendar",
        calendar_event_id=event_id,
        google_event_id=google_event.get("id"),
    )
