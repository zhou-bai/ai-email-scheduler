from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Email and Scheduling Assistant - Backend API"}

@app.get("/api/v1/status")
def get_status():
    return {"status": "running"}