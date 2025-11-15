from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.logging_config import get_logger
from app.models.user import User
from app.schemas.email import EmailProcessRequest, EmailProcessResponse, EmailResponse
from app.services.email_processor import process_unread_emails
from app.services.email_service import delete_email, get_email_by_id, get_user_emails

logger = get_logger(__name__)
router = APIRouter(tags=["emails"])


@router.post("/process", response_model=EmailProcessResponse)
def process_emails(
    request: EmailProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        processed_count, created_events_count, message = process_unread_emails(
            db=db, user_id=current_user.id, max_results=request.max_results
        )
        return EmailProcessResponse(
            success=True,
            processed_count=processed_count,
            created_events_count=created_events_count,
            message=message,
        )
    except Exception as e:  # noqa: BLE001
        logger.error("Error processing emails: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process emails: {e}",
        )


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this email",
        )

    return email


@router.get("/", response_model=List[EmailResponse])
def list_emails(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all emails for a user"""
    return get_user_emails(db, current_user.id, skip, limit)


@router.delete("/{email_id}")
def delete_email_endpoint(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch email to verify ownership
    email = get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    # check ownership
    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this email",
        )

    # Perform deletion
    success = delete_email(db, email_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email",
        )
    return {"success": True, "message": "Email deleted successfully"}
