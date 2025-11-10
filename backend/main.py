# 模块顶部增加导入与初始化
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.infrastructure.token_store import TokenStore
from services.oauth import build_google_auth_url, exchange_code_for_tokens
from services.gmail_client import fetch_new_emails, get_email_content, send_reply
from services.calendar_client import create_event

# 创建 FastAPI 应用实例
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
store = TokenStore()

@app.get("/")
def read_root():
    return {"message": "AI Email and Scheduling Assistant - Backend API"}

@app.get("/api/v1/status")
def get_status():
    return {"status": "running"}

# 新增：获取授权链接
@app.get("/api/v1/auth/google/url")
def get_google_auth_url(user_id: str = Query(..., description="你的系统内部用户ID")):
    try:
        url = build_google_auth_url(user_id)
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 新增：授权回调，交换令牌并保存
@app.get("/api/v1/auth/google/callback")
def google_oauth_callback(code: str, state: str = "", user_id: str = ""):
    try:
        access_token, refresh_token, expiry = exchange_code_for_tokens(code)
        uid = user_id or (state.split(":")[0] if state else "")
        if not uid:
            raise HTTPException(status_code=400, detail="Missing user_id/state")
        store.save_tokens(uid, access_token, refresh_token or "", expiry)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 新增：Gmail 测试接口
@app.get("/api/v1/gmail/new")
def api_gmail_new(user_id: str, max_results: int = 10):
    try:
        return {"messages": fetch_new_emails(user_id, store, max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/gmail/{message_id}")
def api_gmail_get(user_id: str, message_id: str):
    try:
        return get_email_content(user_id, store, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/gmail/{message_id}/reply")
def api_gmail_reply(user_id: str, message_id: str, content: str):
    try:
        return send_reply(user_id, store, message_id, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 新增：Calendar 创建事件
@app.post("/api/v1/calendar/events")
def api_calendar_create(user_id: str, summary: str, start_time: str, end_time: str, timezone: str = "Asia/Shanghai"):
    try:
        body = {"summary": summary, "start_time": start_time, "end_time": end_time, "timezone": timezone}
        return create_event(user_id, store, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))