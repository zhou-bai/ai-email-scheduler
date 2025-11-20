from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate


def create_calendar_event(db: Session, event_data: CalendarEventCreate) -> CalendarEvent:
    """Create a new calendar event record in database"""
    db_event = CalendarEvent(**event_data.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_calendar_event_by_id(db: Session, event_id: int) -> Optional[CalendarEvent]:
    """Get calendar event by ID"""
    return db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()


def get_user_calendar_events(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[CalendarEvent]:
    """Get all calendar events for a user"""
    return (
        db.query(CalendarEvent)
        .filter(CalendarEvent.user_id == user_id)
        .order_by(CalendarEvent.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_calendar_event(
    db: Session, event_id: int, event_data: CalendarEventUpdate
) -> Optional[CalendarEvent]:
    """Update calendar event record"""
    db_event = get_calendar_event_by_id(db, event_id)
    if not db_event:
        return None

    update_data = event_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_calendar_event(db: Session, event_id: int) -> bool:
    """Delete calendar event record and associated email if exists"""
    db_event = get_calendar_event_by_id(db, event_id)
    if not db_event:
        return False

    if db_event.email_id:
        db_email = db.query(Email).filter(Email.id == db_event.email_id).first()
        if db_email:
            db.delete(db_email)

    db.delete(db_event)
    db.commit()
    return True
