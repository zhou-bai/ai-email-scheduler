from typing import Optional, Dict, Any
import logging

# 导入现有的LLM函数
from LLM import generate_email as llm_generate_email
from LLM import analyze_email

logger = logging.getLogger(__name__)


class EmailGenerationService:
    """邮件生成服务"""
    
    @staticmethod
    def generate_email_from_draft(
        subject: Optional[str],
        brief_content: str,
        tone: str,
        recipient_name: Optional[str] = None,
        sender_name: Optional[str] = None,
        purpose: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据简要信息生成完整邮件
        
        Args:
            subject: 邮件主题
            brief_content: 用户输入的简要内容
            tone: 邮件语气 (professional, friendly, formal, casual)
            recipient_name: 收件人姓名
            sender_name: 发件人姓名
            purpose: 邮件目的
            additional_context: 额外上下文信息
            
        Returns:
            {
                "success": bool,
                "data": {
                    "subject": str,
                    "body": str,
                    "body_html": str
                },
                "message": str
            }
        """
        try:
            # 构建生成邮件的输入信息
            email_input = f"""
            简要内容：{brief_content}
            """
            
            if purpose:
                email_input += f"\n邮件目的：{purpose}"
                
            if additional_context:
                email_input += f"\n额外上下文：{additional_context}"
            try:
                analysis = analyze_email(
                    email_content=brief_content,
                    sender=sender_name,
                    subject=subject,
                    recipients=recipient_name,
                )
                if analysis and analysis.get("success"):
                    data = analysis.get("data") or {}
                    event = data.get("event") or ""
                    location = data.get("location") or ""
                    start_time = data.get("start_time")
                    time_text = start_time.isoformat() if start_time else ""
                    if event:
                        email_input += f"\n事件：{event}"
                    if time_text:
                        email_input += f"\n时间：{time_text}"
                    if location:
                        email_input += f"\n地点：{location}"
            except Exception:
                pass
            
            tone_norm = EmailGenerationService.validate_tone(tone)
            # 调用LLM生成邮件
            result = llm_generate_email(
                brief_info=email_input.strip(),
                sender_name=sender_name,
                recipient_name=recipient_name,
                tone=tone_norm
            )
            
            if not result["success"]:
                logger.error(f"LLM邮件生成失败: {result.get('message', '未知错误')}")
                return {
                    "success": False,
                    "data": None,
                    "message": f"邮件生成失败: {result.get('message', '未知错误')}"
                }
            
            # 提取生成的内容
            llm_data = result["data"]
            generated_subject = llm_data.get("subject", subject or "通知")
            generated_content = llm_data.get("content", "")
            
            # 转换为HTML格式
            body_html = EmailGenerationService._convert_to_html(generated_content)
            
            logger.info(f"邮件生成成功 - 主题: {generated_subject}")
            
            return {
                "success": True,
                "data": {
                    "subject": generated_subject,
                    "body": generated_content,
                    "body_html": body_html
                },
                "message": "邮件生成成功"
            }
            
        except Exception as e:
            error_msg = f"邮件生成服务异常: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "data": None,
                "message": error_msg
            }
    
    @staticmethod
    def _convert_to_html(text_content: str) -> str:
        """将纯文本转换为HTML格式"""
        if not text_content:
            return ""
        
        # 简单的文本到HTML转换
        html = text_content.replace('\n', '<br>')
        
        # 包装成完整的HTML文档
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                p {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        return html_doc.strip()
    
    @staticmethod
    def validate_tone(tone: str) -> str:
        """验证并标准化邮件语气"""
        valid_tones = ["professional", "friendly", "formal", "casual"]
        tone_lower = tone.lower().strip()
        
        if tone_lower in valid_tones:
            return tone_lower
        
        # 映射中文语气到英文
        tone_mapping = {
            "专业": "professional",
            "友好": "friendly", 
            "正式": "formal",
            "随意": "casual",
            "职业": "professional",
            "亲切": "friendly"
        }
        
        return tone_mapping.get(tone_lower, "professional")
    
    @staticmethod
    def get_tone_description(tone: str) -> str:
        """获取语气的描述说明"""
        descriptions = {
            "professional": "Professional and business-like tone",
            "friendly": "Warm and approachable tone", 
            "formal": "Very formal and respectful tone",
            "casual": "Relaxed and conversational tone"
        }
        return descriptions.get(tone, "Professional tone")


# 服务实例
email_generation_service = EmailGenerationService()