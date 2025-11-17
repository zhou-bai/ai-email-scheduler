from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.email_recipient import EmailRecipient
from app.schemas.email_recipient import (
    EmailRecipientCreate,
    EmailRecipientUpdate,
    EmailRecipientResponse,
    EmailRecipientListResponse,
)

router = APIRouter(tags=["recipients"])


@router.post("/", response_model=EmailRecipientResponse)
def create_recipient(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recipient_in: EmailRecipientCreate,
):
    existing = (
        db.query(EmailRecipient)
        .filter(EmailRecipient.user_id == current_user.id)
        .filter(EmailRecipient.email == recipient_in.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Recipient email already exists")
    recipient = EmailRecipient(user_id=current_user.id, **recipient_in.model_dump())
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return recipient


@router.get("/", response_model=EmailRecipientListResponse)
def list_recipients(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    query = db.query(EmailRecipient).filter(EmailRecipient.user_id == current_user.id)
    if search:
        query = query.filter(
            (EmailRecipient.name.contains(search))
            | (EmailRecipient.email.contains(search))
            | (EmailRecipient.company.contains(search))
        )
    if is_active is not None:
        query = query.filter(EmailRecipient.is_active == is_active)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total, "page": skip // limit + 1, "size": limit}


@router.get("/{recipient_id}", response_model=EmailRecipientResponse)
def get_recipient(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recipient_id: int,
):
    recipient = (
        db.query(EmailRecipient)
        .filter(EmailRecipient.id == recipient_id, EmailRecipient.user_id == current_user.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient


@router.put("/{recipient_id}", response_model=EmailRecipientResponse)
def update_recipient(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recipient_id: int,
    recipient_in: EmailRecipientUpdate,
):
    recipient = (
        db.query(EmailRecipient)
        .filter(EmailRecipient.id == recipient_id, EmailRecipient.user_id == current_user.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    update_data = recipient_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] is not None:
        exists = (
            db.query(EmailRecipient)
            .filter(EmailRecipient.user_id == current_user.id)
            .filter(EmailRecipient.email == update_data["email"])
            .filter(EmailRecipient.id != recipient_id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Recipient email already exists")
    for k, v in update_data.items():
        setattr(recipient, k, v)
    db.commit()
    db.refresh(recipient)
    return recipient


@router.delete("/{recipient_id}")
def delete_recipient(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recipient_id: int,
):
    recipient = (
        db.query(EmailRecipient)
        .filter(EmailRecipient.id == recipient_id, EmailRecipient.user_id == current_user.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    db.delete(recipient)
    db.commit()
    return {"message": "Recipient deleted"}
