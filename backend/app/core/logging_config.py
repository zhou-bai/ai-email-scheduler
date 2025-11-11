import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    app_name: str = "app",
) -> None:
    log_dir = log_dir or DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, log_level.upper())
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Add handlers
    _add_console_handler(root_logger, level)
    _add_file_handler(root_logger, level, log_dir, app_name)


def _add_console_handler(logger: logging.Logger, level: int) -> None:
    """Add console output handler with ASCII-safe formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_create_formatter())
    logger.addHandler(handler)


def _add_file_handler(
    logger: logging.Logger,
    level: int,
    log_dir: Path,
    app_name: str,
) -> None:
    """Add rotating file handler with date-based naming."""
    log_file = log_dir / _generate_log_filename(app_name)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(_create_formatter())
    logger.addHandler(handler)


def _create_formatter() -> logging.Formatter:
    """Create consistent formatter for all handlers."""
    return logging.Formatter(
        fmt=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )


def _generate_log_filename(app_name: str) -> str:
    """Generate date-based log filename in ASCII-safe format."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    return f"{app_name}_{timestamp}.log"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
