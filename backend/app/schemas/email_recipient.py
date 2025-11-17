from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EmailRecipientBase(BaseModel):
    """收件人基础schema"""
    name: str = Field(..., min_length=1, max_length=100, description="收件人姓名")
    email: EmailStr = Field(..., description="收件人邮箱地址")
    company: Optional[str] = Field(None, max_length=200, description="公司/组织")
    notes: Optional[str] = Field(None, description="备注信息")
    is_active: bool = Field(True, description="是否激活")


class EmailRecipientCreate(EmailRecipientBase):
    """创建收件人"""
    pass


class EmailRecipientUpdate(BaseModel):
    """更新收件人"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class EmailRecipientResponse(EmailRecipientBase):
    """收件人响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmailGenerateRequest(BaseModel):
    """邮件生成请求"""
    recipient_id: Optional[int] = Field(None, description="单个收件人ID")
    recipient_ids: Optional[List[int]] = Field(None, description="多个收件人ID")
    subject: Optional[str] = Field(None, description="邮件主题，可省略让系统自动生成")
    brief_content: str = Field(..., description="用户输入的简要内容")
    tone: str = Field("professional", description="邮件语气：professional, friendly, formal, casual")
    purpose: Optional[str] = Field(None, max_length=100, description="邮件目的")
    additional_context: Optional[str] = Field(None, description="额外的上下文信息")
    sender_name: Optional[str] = Field(None, description="发件人姓名")
    sender_position: Optional[str] = Field(None, description="发件人职位")
    sender_contact: Optional[str] = Field(None, description="发件人联系方式")


class EmailGenerateResponse(BaseModel):
    """邮件生成响应"""
    recipient_id: Optional[int] = None
    recipient_ids: Optional[List[int]] = None
    subject: str
    body: str
    body_html: Optional[str] = None
    success: bool
    message: str


class EmailSendRequest(BaseModel):
    """邮件发送请求"""
    recipient_id: Optional[int] = Field(None, description="单个收件人ID")
    recipient_ids: Optional[List[int]] = Field(None, description="多个收件人ID")
    subject: str = Field(..., min_length=1, max_length=500, description="邮件主题")
    body: str = Field(..., description="邮件正文")
    body_html: Optional[str] = Field(None, description="HTML格式的邮件正文")


class EmailSendResponse(BaseModel):
    """邮件发送响应"""
    success: bool
    message: str
    gmail_message_id: Optional[str] = None
    thread_id: Optional[str] = None


class EmailRecipientListResponse(BaseModel):
    items: List[EmailRecipientResponse]
    total: int
    page: int
    size: int