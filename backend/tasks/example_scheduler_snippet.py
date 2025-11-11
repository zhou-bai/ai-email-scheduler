from backend.infrastructure.db_token_store import DBTokenStore
from backend.services.gmail_client import fetch_new_emails, get_email_content
from backend.services.calendar_client import create_event
from backend.LLM import analyze_email
from datetime import timedelta

store = DBTokenStore()

# 假设任务筛选出要检查的用户，可能是邮箱或DB用户ID
user_key = "kurasa907@gmail.com"  # 或 "123"（DB里的 users.id）
tokens = store.get_tokens(user_key)
if not tokens:
    print("该用户在数据库中未找到令牌，跳过或记录待处理")
else:
    messages = fetch_new_emails(user_key, store, max_results=10)
    if not messages:
        print("没有未读邮件")
    for m in messages:
        content = get_email_content(user_key, store, m["id"])
        is_spam, judge_reason, is_schedule, event, start_dt, end_dt = analyze_email(
            content.get("body_text", ""),
            sender=content.get("from"),
            subject=content.get("subject"),
        )

        if is_spam:
            print(f"跳过垃圾邮件：{content.get('subject')}")
            continue

        print(f"邮件摘要：{judge_reason}")

        if is_schedule and start_dt:
            start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
            end_dt = end_dt or (start_dt + timedelta(hours=1))
            end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

            summary = event or content.get("subject") or "自动识别日程"
            details = {
                "summary": summary,
                "description": (
                    f"来自邮件的自动日程\n"
                    f"发件人：{content.get('from')}\n"
                    f"主题：{content.get('subject')}\n"
                    f"摘要：{judge_reason}"
                ),
                "start_time": start_str,
                "end_time": end_str,
                "timezone": "Asia/Shanghai",
                "attendees": [],
            }
            try:
                created = create_event(user_key, store, details)
                print(f"已创建日程：{summary} -> {created.get('htmlLink')}")
            except Exception as e:
                print(f"创建日程失败：{e}")
        else:
            print("未识别到可创建的日程。")