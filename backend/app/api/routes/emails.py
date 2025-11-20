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
from app.models.email_recipient import EmailRecipient
from app.schemas.email_recipient import (
    EmailGenerateRequest,
    EmailGenerateResponse,
    EmailSendRequest,
    EmailSendResponse,
)
from app.services.email_generation import email_generation_service
from app.services import gmail

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


@router.post("/generate-and-send", response_model=EmailSendResponse)
def generate_and_send_email(
    generate_request: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipients: list[EmailRecipient] = []
    direct_emails: list[str] = []
    if generate_request.to_emails and len(generate_request.to_emails) > 0:
        direct_emails = [str(e) for e in generate_request.to_emails]
    elif generate_request.to_email:
        direct_emails = [str(generate_request.to_email)]
    elif generate_request.recipient_ids:
        recipients = (
            db.query(EmailRecipient)
            .filter(EmailRecipient.user_id == current_user.id)
            .filter(EmailRecipient.id.in_(generate_request.recipient_ids))
            .all()
        )
    elif generate_request.recipient_id is not None:
        r = (
            db.query(EmailRecipient)
            .filter(
                EmailRecipient.id == generate_request.recipient_id,
                EmailRecipient.user_id == current_user.id,
            )
            .first()
        )
        if r:
            recipients = [r]
    if not recipients and not direct_emails:
        raise HTTPException(status_code=404, detail="Recipient not found")

    gen = email_generation_service.generate_email_from_draft(
        subject=generate_request.subject,
        brief_content=generate_request.brief_content,
        tone=generate_request.tone,
        recipient_name=(recipients[0].name if recipients else (direct_emails[0].split("@")[0] if direct_emails else None)),
        sender_name=generate_request.sender_name or current_user.full_name,
        sender_position=generate_request.sender_position,
        sender_contact=generate_request.sender_contact,
        purpose=generate_request.purpose,
        additional_context=generate_request.additional_context,
    )
    if not gen["success"]:
        return {
            "success": False,
            "message": gen.get("message", "Failed to generate email"),
            "gmail_message_id": None,
            "thread_id": None,
        }

    data = gen["data"]
    to_emails = ",".join(direct_emails if direct_emails else [r.email for r in recipients])
    res = gmail.send_email(
        db=db,
        user_id=str(current_user.id),
        to_email=to_emails,
        subject=(data.get("subject") or generate_request.subject or "通知"),
        body=data.get("body", ""),
        body_html=data.get("body_html"),
    )

    return {
        "success": res.get("success", False),
        "message": res.get("message", ""),
        "gmail_message_id": res.get("message_id"),
        "thread_id": res.get("thread_id"),
    }


@router.post("/generate", response_model=EmailGenerateResponse)
def generate_email(
    generate_request: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipients: list[EmailRecipient] = []
    direct_emails: list[str] = []
    if generate_request.to_emails and len(generate_request.to_emails) > 0:
        direct_emails = [str(e) for e in generate_request.to_emails]
    elif generate_request.to_email:
        direct_emails = [str(generate_request.to_email)]
    elif generate_request.recipient_ids:
        recipients = (
            db.query(EmailRecipient)
            .filter(EmailRecipient.user_id == current_user.id)
            .filter(EmailRecipient.id.in_(generate_request.recipient_ids))
            .all()
        )
    elif generate_request.recipient_id is not None:
        r = (
            db.query(EmailRecipient)
            .filter(
                EmailRecipient.id == generate_request.recipient_id,
                EmailRecipient.user_id == current_user.id,
            )
            .first()
        )
        if r:
            recipients = [r]
    if not recipients and not direct_emails:
        raise HTTPException(status_code=404, detail="Recipient not found")

    gen = email_generation_service.generate_email_from_draft(
        subject=generate_request.subject,
        brief_content=generate_request.brief_content,
        tone=generate_request.tone,
        recipient_name=(recipients[0].name if recipients else (direct_emails[0].split("@")[0] if direct_emails else None)),
        sender_name=generate_request.sender_name or current_user.full_name,
        sender_position=generate_request.sender_position,
        sender_contact=generate_request.sender_contact,
        purpose=generate_request.purpose,
        additional_context=generate_request.additional_context,
    )
    if not gen["success"]:
        return {
            "success": False,
            "message": gen.get("message", "Failed to generate email"),
            "recipient_id": generate_request.recipient_id,
            "recipient_ids": generate_request.recipient_ids,
            "subject": generate_request.subject or "",
            "body": "",
            "body_html": None,
        }

    data = gen["data"]
    return {
        "success": True,
        "message": "ok",
        "recipient_id": generate_request.recipient_id,
        "recipient_ids": generate_request.recipient_ids,
        "subject": data.get("subject") or generate_request.subject or "通知",
        "body": data.get("body", ""),
        "body_html": data.get("body_html"),
    }


@router.post("/send", response_model=EmailSendResponse)
def send_email_endpoint(
    send_request: EmailSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipients: list[EmailRecipient] = []
    direct_emails: list[str] = []
    if send_request.to_emails and len(send_request.to_emails) > 0:
        direct_emails = [str(e) for e in send_request.to_emails]
    elif send_request.to_email:
        direct_emails = [str(send_request.to_email)]
    elif send_request.recipient_ids:
        recipients = (
            db.query(EmailRecipient)
            .filter(EmailRecipient.user_id == current_user.id)
            .filter(EmailRecipient.id.in_(send_request.recipient_ids))
            .all()
        )
    elif send_request.recipient_id is not None:
        r = (
            db.query(EmailRecipient)
            .filter(
                EmailRecipient.id == send_request.recipient_id,
                EmailRecipient.user_id == current_user.id,
            )
            .first()
        )
        if r:
            recipients = [r]
    if not recipients and not direct_emails:
        raise HTTPException(status_code=404, detail="Recipient not found")

    to_emails = ",".join(direct_emails if direct_emails else [r.email for r in recipients])
    res = gmail.send_email(
        db=db,
        user_id=str(current_user.id),
        to_email=to_emails,
        subject=send_request.subject,
        body=send_request.body,
        body_html=send_request.body_html,
    )

    return {
        "success": res.get("success", False),
        "message": res.get("message", ""),
        "gmail_message_id": res.get("message_id"),
        "thread_id": res.get("thread_id"),
    }
