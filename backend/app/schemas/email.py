from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class EmailBase(BaseModel):
    email_id: str
    thread_id: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    received_at: Optional[datetime] = None
    snippet: Optional[str] = None
    body_text: Optional[str] = None


class EmailCreate(EmailBase):
    user_id: int


class EmailResponse(EmailBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmailProcessRequest(BaseModel):
    max_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of unread emails to process for current user",
    )


class EmailProcessResponse(BaseModel):
    success: bool
    processed_count: int
    created_events_count: int
    message: str
