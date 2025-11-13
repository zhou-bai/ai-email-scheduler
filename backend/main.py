from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.middleware import LoggingMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import get_logger, setup_logging

setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=Path(settings.LOG_DIR),
    app_name="email_agent",
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database tables initialized successfully")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Powered Email Scheduling and Management API",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "AI Email and Scheduling Assistant - Backend API"}
