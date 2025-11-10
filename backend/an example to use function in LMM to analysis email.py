"""
analyze_email函数：
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
    start_time: datetime;      // 开始时间 (HH:MM 或 "None")
    end_time: datetime;        // 结束时间 (HH:MM 或 "None")
  };
  message?: string;          // 错误信息
}
"""

from LLM import analyze_email
from datetime import datetime, date, time, timedelta

def format_time_display(datetime_obj):
    """格式化时间显示 - 处理 datetime 对象"""
    if datetime_obj is None:
        return "None"
    return datetime_obj.strftime('%Y-%m-%d %H:%M')  # 现在返回完整日期时间

if __name__ == "__main__":
    # Test case 1: Normal work email
    normal_email = """
    Dear Manager Zhang,

    Regarding the project meeting tomorrow at 2:00 PM, I have prepared the relevant materials.
    The meeting will discuss Q3 sales data and market strategy adjustments.
    The meeting is expected to last until 3:30 PM.
    Please confirm if you can attend on time.

    Thank you!
    Assistant Li
    """

    print("=== Test 1: Normal Work Email ===")
    is_spam, reason, has_schedule, event_name, start, end = analyze_email(
        normal_email,
        sender="li.assistant@company.com",
        subject="Project Meeting Confirmation"
    )

    # Process and output results
    print(f"Is spam: {'Yes' if is_spam else 'No'}")
    print(f"Judgment reason/Email summary: {reason}")
    print(f"Contains schedule: {'Yes' if has_schedule else 'No'}")
    print(f"Schedule name: {event_name if event_name else 'None'}")
    print(f"Start time: {format_time_display(start)}")
    print(f"End time: {format_time_display(end)}")
