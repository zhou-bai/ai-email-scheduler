from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CalendarEventBase(BaseModel):
    summary: str
    location: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: Optional[str] = None


class CalendarEventCreate(CalendarEventBase):
    user_id: int


class CalendarEventUpdate(BaseModel):
    summary: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[str] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConfirmScheduleRequest(BaseModel):
    email_id: int = Field(..., description="Email record ID in database")
    user_id: int = Field(..., description="User ID")


class ConfirmScheduleResponse(BaseModel):
    success: bool
    message: str
    calendar_event_id: Optional[int] = None
    google_event_id: Optional[str] = None
