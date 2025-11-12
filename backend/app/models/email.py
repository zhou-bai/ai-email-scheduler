from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    email_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), index=True, default=None)

    from_address: Mapped[str | None] = mapped_column(String(320), default=None)
    to_address: Mapped[str | None] = mapped_column(String(512), default=None)
    subject: Mapped[str | None] = mapped_column(String(512), default=None)
    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, default=None
    )
    snippet: Mapped[str | None] = mapped_column(Text, default=None)
    body_text: Mapped[str | None] = mapped_column(Text, default=None)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, email_id='{self.email_id}', subject='{self.subject}')>"
