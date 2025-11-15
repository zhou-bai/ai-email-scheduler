from openai import OpenAI
from datetime import datetime, timedelta
import re

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-9faaade8e44b4b7e8f0f8ee2f093de46",
    base_url="https://api.deepseek.com"
)


def analyze_email(email_content, sender=None, subject=None, recipients=None):
    """
    分析邮件内容，判断是否为垃圾邮件并提取日程信息

    输入：
    {
      email_content: string;  // 必需，邮件正文
      sender?: string;        // 可选，发件人
      subject?: string;       // 可选，邮件主题
    }

    输出：
    {
      success: boolean;
      data: {
        is_spam: boolean;        // 是否为垃圾邮件
        judge_reason: string;    // 是-判断垃圾邮件的理由/否-邮件总结
        is_schedule: boolean;    // 是否包含日程
        event: string;           // 日程名称
        start_time: datetime;    // 开始时间
        end_time: datetime;      // 结束时间
        location: string;        // 会议地点
        participants: string;    // 参会人员
      };
      message?: string;          // 错误信息
    }
    """
    # Build system prompt - 增强版，要求返回日期信息和参会详情
    system_prompt = """You are a professional email management assistant. Your tasks are:
    1. Determine if the email is spam/advertisement
    2. If it's a normal email, provide a concise and accurate summary
    3. If it's spam, explain the reasoning
    
    Judgment criteria:
    - Spam characteristics: promotional ads, investment offers, lottery winning information, suspicious links, many grammatical errors, urgent tone
    - Normal email characteristics: work communication, personal letters, official notifications, specific and clear content
    
    4. Extract schedule information including date and time
    5. Extract meeting location if mentioned
    6. Extract participants if mentioned. When email addresses are available (in content or headers), list participants as "Name <email>"; if no email is available, list names only. Separate multiple participants with commas.
    
    Please respond in the following format:
    【Spam Judgment】：Yes/No
    【Judgment Reason】：Briefly explain the reason
    【Email Summary】：If it's a normal email, summarize the main content; if it's spam, mark as "No action needed"
    【Contains Schedule】：Yes/No
    【Schedule Name】：Briefly summarize the schedule content, output "None" if no schedule
    【Start Time】：Format strictly as "10:00", 24-hour format, output "None" if no schedule, output "Unknown" if start time is known but end time is unknown
    【End Time】：Format strictly as "10:00", 24-hour format, output "None" if no schedule, output "Unknown" if end time is unknown
    【Schedule Date】：Format strictly as "YYYY-MM-DD", output "None" if no date mentioned, output "Today" if today, output "Tomorrow" if tomorrow, or specific date like "2024-01-20"
    【Meeting Location】：Extract meeting location if mentioned, output "None" if no location mentioned
    【Participants】：Extract participants if mentioned (names, roles, or groups), output "None" if no participants mentioned
    """

    # Build user message
    user_message = f"Please analyze the following email:\n"
    if subject:
        user_message += f"Subject: {subject}\n"
    if sender:
        user_message += f"Sender: {sender}\n"
    if recipients:
        user_message += f"Recipients: {recipients}\n"
    user_message += f"Content: {email_content}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )

        result_text = response.choices[0].message.content
        return parse_api_response(result_text)

    except Exception as e:
        error_message = f"Analysis failed: {e}"
        print(error_message)
        return {
            "success": False,
            "data": None,
            "message": error_message
        }


def generate_email(brief_info, sender_name=None, recipient_name=None, tone="professional"):
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
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )

        result_text = response.choices[0].message.content
        return parse_email_generation_response(result_text)

    except Exception as e:
        error_message = f"Email generation failed: {e}"
        print(error_message)
        return {
            "success": False,
            "data": None,
            "message": error_message
        }


def parse_api_response(response_text):
    """
    解析API返回的文本，提取所需信息
    """
    try:
        spam_match = re.search(r'【Spam Judgment】：(Yes|No)', response_text)
        reason_match = re.search(r'【Judgment Reason】：(.*?)(?=【|$)', response_text, re.DOTALL)
        summary_match = re.search(r'【Email Summary】：(.*?)(?=【|$)', response_text, re.DOTALL)
        schedule_match = re.search(r'【Contains Schedule】：(Yes|No)', response_text)
        event_match = re.search(r'【Schedule Name】：(.*?)(?=【|$)', response_text, re.DOTALL)
        start_match = re.search(r'【Start Time】：(.*?)(?=【|$)', response_text, re.DOTALL)
        end_match = re.search(r'【End Time】：(.*?)(?=【|$)', response_text, re.DOTALL)
        date_match = re.search(r'【Schedule Date】：(.*?)(?=【|$)', response_text, re.DOTALL)
        location_match = re.search(r'【Meeting Location】：(.*?)(?=【|$)', response_text, re.DOTALL)
        participants_match = re.search(r'【Participants】：(.*?)(?=【|$)', response_text, re.DOTALL)

        # 提取基本信息
        is_spam = spam_match.group(1) == 'Yes' if spam_match else False

        judge_reason = ""
        if reason_match:
            judge_reason = reason_match.group(1).strip()
        elif summary_match:
            judge_reason = summary_match.group(1).strip()

        is_schedule = schedule_match.group(1) == 'Yes' if schedule_match else False

        event = ""
        if event_match:
            event = event_match.group(1).strip()
            if event == 'None':
                event = ""

        # 解析日期信息
        schedule_date = None
        if date_match:
            date_str = date_match.group(1).strip()
            if date_str not in ['None', 'Unknown']:
                schedule_date = parse_date_from_string(date_str)

        # 获取基准日期（优先使用邮件中的日期，没有则使用当天）
        base_date = schedule_date if schedule_date else datetime.now().date()

        start_time = None
        if start_match:
            start_str = start_match.group(1).strip()
            if start_str not in ['None', 'Unknown']:
                try:
                    time_part = datetime.strptime(start_str, '%H:%M').time()
                    start_time = datetime.combine(base_date, time_part)
                except ValueError:
                    pass

        end_time = None
        if end_match:
            end_str = end_match.group(1).strip()
            if end_str not in ['None', 'Unknown']:
                try:
                    time_part = datetime.strptime(end_str, '%H:%M').time()
                    end_time = datetime.combine(base_date, time_part)
                except ValueError:
                    pass

        # 提取地点信息
        location = ""
        if location_match:
            location = location_match.group(1).strip()
            if location == 'None':
                location = ""

        # 提取参会人员信息
        participants = ""
        if participants_match:
            participants = participants_match.group(1).strip()
            if participants == 'None':
                participants = ""

        # 构建返回数据
        data = {
            "is_spam": is_spam,
            "judge_reason": judge_reason,
            "is_schedule": is_schedule,
            "event": event,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "participants": participants
        }

        return {
            "success": True,
            "data": data,
            "message": "Analysis completed successfully"
        }

    except Exception as e:
        error_message = f"Failed to parse API response: {e}"
        print(error_message)
        return {
            "success": False,
            "data": None,
            "message": error_message
        }


def parse_email_generation_response(response_text):
    """
    解析邮件生成API返回的文本
    """
    try:
        subject_match = re.search(r'【Email Subject】：(.*?)(?=【|$)', response_text, re.DOTALL)
        content_match = re.search(r'【Email Content】：(.*?)(?=【|$)', response_text, re.DOTALL)

        subject = ""
        content = ""

        if subject_match:
            subject = subject_match.group(1).strip()

        if content_match:
            content = content_match.group(1).strip()

        # 如果正则匹配失败，尝试其他方式提取
        if not subject or not content:
            lines = response_text.split('\n')
            subject_found = False
            content_lines = []

            for line in lines:
                if 'Email Subject' in line or '主题' in line:
                    subject = line.split('：')[-1].strip()
                    subject_found = True
                elif subject_found and line.strip():
                    content_lines.append(line)

            if content_lines:
                content = '\n'.join(content_lines)

        # 构建返回数据
        data = {
            "subject": subject,
            "content": content
        }

        return {
            "success": True,
            "data": data,
            "message": "Email generated successfully"
        }

    except Exception as e:
        error_message = f"Failed to parse email generation response: {e}"
        print(error_message)
        return {
            "success": False,
            "data": None,
            "message": error_message
        }


def parse_date_from_string(date_str):
    """
    解析日期字符串，支持多种格式
    """
    try:
        date_str = date_str.strip()

        # 处理特殊关键词
        if date_str.lower() == 'today':
            return datetime.now().date()
        elif date_str.lower() == 'tomorrow':
            return (datetime.now() + timedelta(days=1)).date()

        # 尝试解析标准日期格式
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

        # 尝试其他常见日期格式
        date_formats = [
            '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y',
            '%B %d, %Y', '%b %d, %Y'  # January 15, 2024 或 Jan 15, 2024
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
    return datetime_obj.strftime('%Y-%m-%d %H:%M')


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
        print("Reason:", data["judge_reason"])
        print("Has schedule:", data["is_schedule"])
        print("Event:", data["event"])
        print("Start time:", format_time_display(data["start_time"]))
        print("End time:", format_time_display(data["end_time"]))
        print("Location:", data["location"])
        print("Participants:", data["participants"])
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
        tone="professional"
    )

    print("Success:", result2["success"])
    if result2["success"]:
        data = result2["data"]
        print("Generated Subject:", data["subject"])
        print("Generated Content:")
        print(data["content"])
    else:
        print("Error:", result2["message"])