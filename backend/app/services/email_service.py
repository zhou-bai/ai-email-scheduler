from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.email import Email
from app.schemas.email import EmailCreate


def create_email(db: Session, email_data: EmailCreate) -> Email:
    """Create a new email record in database"""
    db_email = Email(**email_data.model_dump())
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email


def get_email_by_id(db: Session, email_id: int) -> Optional[Email]:
    """Get email by database ID"""
    return db.query(Email).filter(Email.id == email_id).first()


def get_email_by_email_id(db: Session, email_id: str) -> Optional[Email]:
    """Get email by Gmail message ID"""
    return db.query(Email).filter(Email.email_id == email_id).first()


def get_user_emails(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Email]:
    """Get all emails for a user"""
    return (
        db.query(Email)
        .filter(Email.user_id == user_id)
        .order_by(Email.received_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_email(db: Session, email_id: int, **kwargs) -> Optional[Email]:
    """Update email record"""
    db_email = get_email_by_id(db, email_id)
    if not db_email:
        return None

    for key, value in kwargs.items():
        if hasattr(db_email, key):
            setattr(db_email, key, value)

    db.commit()
    db.refresh(db_email)
    return db_email


def delete_email(db: Session, email_id: int) -> bool:
    """Delete email record, but only if no calendar events are associated"""
    from app.models.calendar import CalendarEvent

    db_email = get_email_by_id(db, email_id)
    if not db_email:
        return False

    linked_events_count = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.email_id == email_id)
        .count()
    )

    if linked_events_count > 0:
        raise ValueError(
            f"Cannot delete email: {linked_events_count} calendar event(s) still linked. "
            f"Delete all associated events first."
        )

    db.delete(db_email)
    db.commit()
    return True
