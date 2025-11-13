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
    start_time: datetime;    // 开始时间
    end_time: datetime;      // 结束时间
    location: string;        // 会议地点
    participants: string;    // 参会人员
  };
  message?: string;          // 错误信息
}

generate_email函数：
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

from LLM import analyze_email, generate_email
from datetime import datetime

def format_time_display(datetime_obj):
    """格式化时间显示 - 处理 datetime 对象"""
    if datetime_obj is None:
        return "None"
    return datetime_obj.strftime('%Y-%m-%d %H:%M')  # 现在返回完整日期时间

if __name__ == "__main__":
    # Test case 1: Normal work email analysis
    normal_email = """
    Dear Manager Zhang,

    Regarding the project meeting tomorrow at 2:00 PM, I have prepared the relevant materials.
    The meeting will discuss Q3 sales data and market strategy adjustments.
    The meeting is expected to last until 3:30 PM.
    Please confirm if you can attend on time.

    Thank you!
    Assistant Li
    """

    print("=== Test 1: Normal Work Email Analysis ===")
    result = analyze_email(
        normal_email,
        sender="li.assistant@company.com",
        subject="Project Meeting Confirmation"
    )

    # Process and output results
    print(f"Success: {result['success']}")
    if result['success']:
        data = result['data']
        print(f"Is spam: {'Yes' if data['is_spam'] else 'No'}")
        print(f"Judgment reason/Email summary: {data['judge_reason']}")
        print(f"Contains schedule: {'Yes' if data['is_schedule'] else 'No'}")
        print(f"Schedule name: {data['event'] if data['event'] else 'None'}")
        print(f"Start time: {format_time_display(data['start_time'])}")
        print(f"End time: {format_time_display(data['end_time'])}")
        print(f"Location: {data['location']}")
        print(f"Participants: {data['participants']}")
    else:
        print(f"Error: {result['message']}")

    print("\n" + "=" * 50 + "\n")

    # Test case 2: Email generation - meeting notification
    print("=== Test 2: Email Generation - Meeting Notification ===")
    meeting_info = "通知团队成员明天下午2点开会讨论项目进展，需要准备进度报告，会议地点在301会议室"
    result2 = generate_email(
        brief_info=meeting_info,
        sender_name="张经理",
        recipient_name="项目团队全体成员",
        tone="professional"
    )

    print(f"Success: {result2['success']}")
    if result2['success']:
        data = result2['data']
        print(f"Generated Subject: {data['subject']}")
        print("Generated Content:")
        print(data['content'])
    else:
        print(f"Error: {result2['message']}")

    print("\n" + "=" * 50 + "\n")

    # Test case 3: Email generation - casual invitation
    print("=== Test 3: Email Generation - Casual Invitation ===")
    party_info = "邀请同事参加周五晚上的团队聚餐，地点在公司附近的火锅店，时间是晚上6点半"
    result3 = generate_email(
        brief_info=party_info,
        sender_name="小李",
        recipient_name="同事们",
        tone="casual"
    )

    print(f"Success: {result3['success']}")
    if result3['success']:
        data = result3['data']
        print(f"Generated Subject: {data['subject']}")
        print("Generated Content:")
        print(data['content'])
    else:
        print(f"Error: {result3['message']}")

    print("\n" + "=" * 50 + "\n")

    # Test case 4: Email generation - formal request
    print("=== Test 4: Email Generation - Formal Request ===")
    request_info = "meeting,important,about the final project,everyone should come,2:00-3:00"
    result4 = generate_email(
        brief_info=request_info,
        sender_name="Mr Wang",
        recipient_name="Miss Li",
        tone="formal"
    )

    print(f"Success: {result4['success']}")
    if result4['success']:
        data = result4['data']
        print(f"Generated Subject: {data['subject']}")
        print("Generated Content:")
        print(data['content'])
    else:
        print(f"Error: {result4['message']}")