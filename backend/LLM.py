from openai import OpenAI
from datetime import datetime, timedelta
import json

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-9faaade8e44b4b7e8f0f8ee2f093de46", base_url="https://api.deepseek.com"
)


def analyze_email(email_content, sender=None, subject=None, recipients=None):
    """
    Analyze email content to detect spam and extract multiple schedule events.

    Returns:
    {
      success: boolean,
      data: {
        is_spam: boolean,
        summary: string,
        has_schedule: boolean,
        events: [
          {
            name: string,
            date: string,
            start_time: string,
            end_time: string,
            location: string,
            participants: string
          }
        ]
      },
      message?: string
    }
    """
    system_prompt = """You are a professional email management assistant. Analyze emails and return structured JSON output.

Tasks:
1. Detect spam/advertisements
2. Provide email summary (or spam detection reason if spam)
3. Extract ALL schedule events from the email (an email may contain multiple events)
4. For each event, extract: name, date, time range, location, and participants

Spam detection criteria:
- Spam: promotional ads, investment offers, lottery wins, suspicious links, poor grammar, urgent/threatening tone
- Normal: work communication, personal messages, official notifications, clear specific content

You MUST respond with valid JSON in this exact structure:
{
  "is_spam": false,
  "summary": "Brief email summary or spam reason",
  "has_schedule": true,
  "events": [
    {
      "name": "Event title",
      "date": "2025-01-20 or Today or Tomorrow",
      "start_time": "09:00",
      "end_time": "11:00",
      "location": "Conference Room A or empty string",
      "participants": "Name <email@example.com>, Name2 or empty string"
    }
  ]
}

Rules:
- If no events: "events": []
- Date format: "YYYY-MM-DD" or "Today" or "Tomorrow"
- Time format: "HH:MM" (24-hour)
- Empty fields: use empty string "", NOT null or "None"
- Multiple events: list all in the events array"""

    # Build user message
    user_message = "Please analyze the following email:\n"
    if subject:
        user_message += f"Subject: {subject}\n"
    if sender:
        user_message += f"Sender: {sender}\n"
    if recipients:
        user_message += f"Recipients: {recipients}\n"
    user_message += f"Content: {email_content}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={"type": "json_object"},
            stream=False,
        )

        result_text = response.choices[0].message.content
        return parse_json_response(result_text)

    except Exception as e:
        error_message = f"Analysis failed: {e}"
        print(error_message)
        return {"success": False, "data": None, "message": error_message}


def generate_email(
    brief_info, sender_name=None, recipient_name=None, tone="professional"
):
    """
    根据简要信息生成完整的邮件主题和内容

    输入：
    {
      brief_info: string;       // 必需，邮件的简要信息
      sender_name?: string;     // 可选，发件人姓名
      recipient_name?: string;  // 可选，收件人姓名
      tone?: string;           // 可选，邮件语气，如 "professional", "casual", "formal"
    }

    输出：
    {
      success: boolean;
      data: {
        subject: string;        // 生成的邮件主题
        content: string;        // 生成的完整邮件内容
      };
      message?: string;         // 错误信息
    }
    """
    # Build system prompt for email generation
    system_prompt = """You are a professional email writing assistant. Your task is to generate a complete email based on brief information provided by the user.

    Requirements:
    1. Generate a clear and appropriate email subject
    2. Write a complete, well-structured email body
    3. Adapt the tone based on the user's requirement (professional, casual, formal, etc.)
    4. Include appropriate greetings and closing
    5. Make the email coherent and easy to understand
    
    Please respond in the following format:
    【Email Subject】：Generated email subject
    【Email Content】：Complete email content with proper formatting
    """

    # Build user message
    user_message = f"Please generate an email based on the following information:\n"
    user_message += f"Brief information: {brief_info}\n"
    if sender_name:
        user_message += f"Sender name: {sender_name}\n"
    if recipient_name:
        user_message += f"Recipient name: {recipient_name}\n"
    user_message += f"Tone: {tone}\n"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, stream=False
        )

        result_text = response.choices[0].message.content
        return parse_email_generation_response(result_text)

    except Exception as e:
        error_message = f"Email generation failed: {e}"
        print(error_message)
        return {"success": False, "data": None, "message": error_message}


def parse_json_response(response_text):
    """Parse JSON response from DeepSeek API and convert to internal format"""
    try:
        data = json.loads(response_text)

        is_spam = data.get("is_spam", False)
        summary = data.get("summary", "")
        has_schedule = data.get("has_schedule", False)
        events_raw = data.get("events", [])

        events = []
        for event_raw in events_raw:
            event_name = event_raw.get("name", "")
            date_str = event_raw.get("date", "")
            start_time_str = event_raw.get("start_time", "")
            end_time_str = event_raw.get("end_time", "")
            location = event_raw.get("location", "")
            participants = event_raw.get("participants", "")

            event_date = parse_date_from_string(date_str)
            if not event_date:
                event_date = datetime.now().date()

            start_time = None
            if start_time_str:
                try:
                    time_part = datetime.strptime(start_time_str, "%H:%M").time()
                    start_time = datetime.combine(event_date, time_part)
                except ValueError:
                    pass

            end_time = None
            if end_time_str:
                try:
                    time_part = datetime.strptime(end_time_str, "%H:%M").time()
                    end_time = datetime.combine(event_date, time_part)
                except ValueError:
                    pass

            if event_name or start_time:
                events.append(
                    {
                        "event_name": event_name,
                        "start_time": start_time,
                        "end_time": end_time,
                        "location": location,
                        "participants": participants,
                    }
                )

        return {
            "success": True,
            "data": {
                "is_spam": is_spam,
                "judge_reason": summary,
                "is_schedule": has_schedule and len(events) > 0,
                "events": events,
            },
        }

    except json.JSONDecodeError as e:
        error_message = f"Failed to parse JSON response: {e}"
        print(error_message)
        return {"success": False, "data": None, "message": error_message}
    except Exception as e:
        error_message = f"Failed to parse API response: {e}"
        print(error_message)
        return {"success": False, "data": None, "message": error_message}


def parse_email_generation_response(response_text):
    """
    解析邮件生成API返回的文本
    """
    try:
        subject_match = re.search(
            r"【Email Subject】：(.*?)(?=【|$)", response_text, re.DOTALL
        )
        content_match = re.search(
            r"【Email Content】：(.*?)(?=【|$)", response_text, re.DOTALL
        )

        subject = ""
        content = ""

        if subject_match:
            subject = subject_match.group(1).strip()

        if content_match:
            content = content_match.group(1).strip()

        # 如果正则匹配失败，尝试其他方式提取
        if not subject or not content:
            lines = response_text.split("\n")
            subject_found = False
            content_lines = []

            for line in lines:
                if "Email Subject" in line or "主题" in line:
                    subject = line.split("：")[-1].strip()
                    subject_found = True
                elif subject_found and line.strip():
                    content_lines.append(line)

            if content_lines:
                content = "\n".join(content_lines)

        # 构建返回数据
        data = {"subject": subject, "content": content}

        return {
            "success": True,
            "data": data,
        }

    except Exception as e:
        error_message = f"Failed to parse email generation response: {e}"
        print(error_message)
        return {"success": False, "data": None, "message": error_message}


def parse_date_from_string(date_str):
    """
    解析日期字符串，支持多种格式
    """
    try:
        date_str = date_str.strip()

        # 处理特殊关键词
        if date_str.lower() == "today":
            return datetime.now().date()
        elif date_str.lower() == "tomorrow":
            return (datetime.now() + timedelta(days=1)).date()

        # 尝试解析标准日期格式
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

        # 尝试其他常见日期格式
        date_formats = [
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%b %d, %Y",  # January 15, 2024 或 Jan 15, 2024
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    except Exception:
        return None


def format_time_display(datetime_obj):
    """格式化时间显示 - 处理 datetime 对象"""
    if datetime_obj is None:
        return "None"
    return datetime_obj.strftime("%Y-%m-%d %H:%M")


# 测试代码
if __name__ == "__main__":
    # 测试用例1：包含具体日期的邮件
    test_email1 = """
    Dear colleagues,
    The quarterly summary meeting will be held on 2024-01-20 in Conference Room A from 9:00 AM to 11:00 AM.
    Please attend on time and prepare relevant reports.
    Attendees: John, Mary, David, and Lisa from Sales Department.
    HR Department
    """

    print("=== 测试1：包含具体日期的邮件 ===")
    result1 = analyze_email(test_email1, "hr@company.com", "Quarterly Meeting")
    print("Success:", result1["success"])
    if result1["success"]:
        data = result1["data"]
        print("Is spam:", data["is_spam"])
        print("Summary:", data["judge_reason"])
        print("Has schedule:", data["is_schedule"])
        print(f"Events count: {len(data.get('events', []))}")
        for i, event in enumerate(data.get("events", []), 1):
            print(f"\nEvent {i}:")
            print("  Name:", event["event_name"])
            print("  Start time:", format_time_display(event["start_time"]))
            print("  End time:", format_time_display(event["end_time"]))
            print("  Location:", event["location"])
            print("  Participants:", event["participants"])
    else:
        print("Error:", result1["message"])

    print("\n" + "=" * 50 + "\n")

    # 测试用例2：测试邮件生成功能
    print("=== 测试2：邮件生成功能 ===")
    brief_info = "通知团队成员明天下午2点开会讨论项目进展，需要准备进度报告，说英文"
    result2 = generate_email(
        brief_info=brief_info,
        sender_name="张经理",
        recipient_name="项目团队",
        tone="professional",
    )

    print("Success:", result2["success"])
    if result2["success"]:
        data = result2["data"]
        print("Generated Subject:", data["subject"])
        print("Generated Content:")
        print(data["content"])
    else:
        print("Error:", result2["message"])
