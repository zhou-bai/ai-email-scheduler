from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any, Dict, List
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.oauth import get_fresh_token


def fetch_emails(
    db: Session, user_id: str, max_results: int = 10
) -> List[Dict[str, Any]]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    result = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results)
        .execute()
    )
    return result.get("messages", [])


def get_email(db: Session, user_id: str, email_id: str) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=email_id, format="full")
        .execute()
    )

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body_text = _extract_body(msg.get("payload", {}))

    return {
        "id": email_id,
        "threadId": msg.get("threadId"),
        "snippet": msg.get("snippet"),
        "from": headers.get("From"),
        "to": headers.get("To"),
        "subject": headers.get("Subject"),
        "date": headers.get("Date"),
        "body_text": body_text,
    }


def reply_email(
    db: Session, user_id: str, email_id: str, content: str
) -> Dict[str, Any]:
    creds = _get_creds(db, user_id)
    service = build("gmail", "v1", credentials=creds)
    original = (
        service.users()
        .messages()
        .get(userId="me", id=email_id, format="full")
        .execute()
    )

    headers = {
        h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])
    }
    to_addr = headers.get("From")
    subject = headers.get("Subject", "(no subject)")
    message_id = headers.get("Message-Id") or headers.get("Message-ID")

    mime_msg = email.message.EmailMessage()
    mime_msg["To"] = to_addr
    mime_msg["Subject"] = f"Re: {subject}"
    if message_id:
        mime_msg["In-Reply-To"] = message_id
        mime_msg["References"] = message_id
    mime_msg.set_content(content)

    raw = urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    return (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw, "threadId": original.get("threadId")})
        .execute()
    )


def _get_creds(db: Session, user_id: str) -> Credentials:
    access_token = get_fresh_token(db, user_id)
    creds = Credentials(
        access_token,
        token_uri=settings.GOOGLE_TOKEN_URI,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GOOGLE_SCOPES,
    )
    return creds


def _extract_body(payload: Dict[str, Any]) -> str:
    d = payload.get("body", {}).get("data")
    if d:
        return urlsafe_b64decode(d.encode("utf-8")).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            d = part.get("body", {}).get("data")
            if d:
                return urlsafe_b64decode(d.encode("utf-8")).decode(
                    "utf-8", errors="ignore"
                )
    return ""


def send_email(
    db: Session, user_id: str, to_email: str, subject: str, 
    body: str, body_html: str = None, cc: str = None, bcc: str = None
) -> Dict[str, Any]:
    """
    发送邮件
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 纯文本邮件内容
        body_html: HTML邮件内容（可选）
        cc: 抄送邮箱（可选）
        bcc: 密送邮箱（可选）
        
    Returns:
        {
            "success": bool,
            "message_id": str,
            "thread_id": str,
            "message": str
        }
    """
    try:
        creds = _get_creds(db, user_id)
        service = build("gmail", "v1", credentials=creds)
        
        # 创建邮件消息
        mime_msg = email.message.EmailMessage()
        mime_msg["To"] = to_email
        mime_msg["Subject"] = subject
        
        if cc:
            mime_msg["Cc"] = cc
        if bcc:
            mime_msg["Bcc"] = bcc
        
        # 设置纯文本内容
        mime_msg.set_content(body)
        
        # 如果有HTML内容，添加为替代内容
        if body_html:
            mime_msg.add_alternative(body_html, subtype='html')
        
        # 编码消息
        raw = urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
        
        # 发送邮件
        result = service.users().messages().send(
            userId="me", 
            body={"raw": raw}
        ).execute()
        
        return {
            "success": True,
            "message_id": result.get("id"),
            "thread_id": result.get("threadId"),
            "message": "邮件发送成功"
        }
        
    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}"
        return {
            "success": False,
            "message_id": None,
            "thread_id": None,
            "message": error_msg
        }
