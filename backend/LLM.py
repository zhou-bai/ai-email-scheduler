from openai import OpenAI
from datetime import datetime, timedelta
import re

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-9faaade8e44b4b7e8f0f8ee2f093de46",
    base_url="https://api.deepseek.com"
)


def analyze_email(email_content, sender=None, subject=None):
    """
    分析邮件内容，判断是否为垃圾邮件并提取日程信息
    """
    # Build system prompt - 增强版，要求返回日期信息
    system_prompt = """You are a professional email management assistant. Your tasks are:
1. Determine if the email is spam/advertisement
2. If it's a normal email, provide a concise and accurate summary
3. If it's spam, explain the reasoning

Judgment criteria:
- Spam characteristics: promotional ads, investment offers, lottery winning information, suspicious links, many grammatical errors, urgent tone
- Normal email characteristics: work communication, personal letters, official notifications, specific and clear content

4. Extract schedule information including date and time

Please respond in the following format:
【Spam Judgment】：Yes/No
【Judgment Reason】：Briefly explain the reason
【Email Summary】：If it's a normal email, summarize the main content; if it's spam, mark as "No action needed"
【Contains Schedule】：Yes/No
【Schedule Name】：Briefly summarize the schedule content, output "None" if no schedule
【Start Time】：Format strictly as "10:00", 24-hour format, output "None" if no schedule, output "Unknown" if start time is known but end time is unknown
【End Time】：Format strictly as "10:00", 24-hour format, output "None" if no schedule, output "Unknown" if end time is unknown
【Schedule Date】：Format strictly as "YYYY-MM-DD", output "None" if no date mentioned, output "Today" if today, output "Tomorrow" if tomorrow, or specific date like "2024-01-20"
"""

    # Build user message
    user_message = f"Please analyze the following email:\n"
    if subject:
        user_message += f"Subject: {subject}\n"
    if sender:
        user_message += f"Sender: {sender}\n"
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
        print(f"Analysis failed: {e}")
        return False, f"Analysis failed: {e}", False, "", None, None


def parse_api_response(response_text):
    """
    解析API返回的文本，提取所需信息
    """
    is_spam = False
    judge_reason = ""
    is_schedule = False
    event = ""
    start_time = None
    end_time = None

    try:
        spam_match = re.search(r'【Spam Judgment】：(Yes|No)', response_text)
        reason_match = re.search(r'【Judgment Reason】：(.*?)(?=【|$)', response_text, re.DOTALL)
        summary_match = re.search(r'【Email Summary】：(.*?)(?=【|$)', response_text, re.DOTALL)
        schedule_match = re.search(r'【Contains Schedule】：(Yes|No)', response_text)
        event_match = re.search(r'【Schedule Name】：(.*?)(?=【|$)', response_text, re.DOTALL)
        start_match = re.search(r'【Start Time】：(.*?)(?=【|$)', response_text, re.DOTALL)
        end_match = re.search(r'【End Time】：(.*?)(?=【|$)', response_text, re.DOTALL)
        date_match = re.search(r'【Schedule Date】：(.*?)(?=【|$)', response_text, re.DOTALL)

        if spam_match:
            is_spam = spam_match.group(1) == 'Yes'

        if reason_match:
            judge_reason = reason_match.group(1).strip()
        elif summary_match:
            judge_reason = summary_match.group(1).strip()

        if schedule_match:
            is_schedule = schedule_match.group(1) == 'Yes'

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

        if start_match:
            start_str = start_match.group(1).strip()
            if start_str not in ['None', 'Unknown']:
                try:
                    # 创建完整的 datetime 对象
                    time_part = datetime.strptime(start_str, '%H:%M').time()
                    start_time = datetime.combine(base_date, time_part)
                except ValueError:
                    pass

        if end_match:
            end_str = end_match.group(1).strip()
            if end_str not in ['None', 'Unknown']:
                try:
                    # 创建完整的 datetime 对象
                    time_part = datetime.strptime(end_str, '%H:%M').time()
                    end_time = datetime.combine(base_date, time_part)
                except ValueError:
                    pass

        return is_spam, judge_reason, is_schedule, event, start_time, end_time

    except Exception as e:
        print(f"Failed to parse API response: {e}")
        return False, f"Parse failed: {e}", False, "", None, None


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
    return datetime_obj.strftime('%Y-%m-%d %H:%M')  # 现在返回完整日期时间


# 测试代码
if __name__ == "__main__":
    # 测试用例1：包含具体日期的邮件
    test_email1 = """
    Dear colleagues,
    The quarterly summary meeting will be held on 2024-01-20 in Conference Room A from 9:00 AM to 11:00 AM.
    Please attend on time and prepare relevant reports.
    HR Department
    """

    print("=== 测试1：包含具体日期的邮件 ===")
    result1 = analyze_email(test_email1, "hr@company.com", "Quarterly Meeting")
    print("测试结果:", result1)
    if result1[4]:  # start_time
        print("开始时间:", format_time_display(result1[4]))
    if result1[5]:  # end_time
        print("结束时间:", format_time_display(result1[5]))

    print("\n" + "=" * 50 + "\n")

    # 测试用例2：使用相对日期的邮件
    test_email2 = """
    Hello team,
    Let's have a quick sync tomorrow at 14:30 to discuss the project updates.
    The meeting should last about 1 hour.
    Best regards,
    Project Manager
    """

    print("=== 测试2：使用相对日期的邮件 ===")
    result2 = analyze_email(test_email2, "pm@company.com", "Project Sync")
    print("测试结果:", result2)
    if result2[4]:  # start_time
        print("开始时间:", format_time_display(result2[4]))
    if result2[5]:  # end_time
        print("结束时间:", format_time_display(result2[5]))

    print("\n" + "=" * 50 + "\n")

    # 测试用例3：没有日期的邮件
    test_email3 = """
    Hi all,
    We need to schedule a code review at 16:00.
    Please let me know if you can make it.
    Thanks,
    Tech Lead
    """

    print("=== 测试3：没有日期的邮件 ===")
    result3 = analyze_email(test_email3, "tech@company.com", "Code Review")
    print("测试结果:", result3)
    if result3[4]:  # start_time
        print("开始时间:", format_time_display(result3[4]))
    if result3[5]:  # end_time
        print("结束时间:", format_time_display(result3[5]))