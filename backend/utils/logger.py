"""
Logging configuration for Project Eden V2
"""
import sys
from loguru import logger
from pathlib import Path

# Remove default logger
logger.remove()

# Add console logger with formatting
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Add file logger for errors
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "eden_errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)

# Add file logger for all logs
logger.add(
    log_dir / "eden_all.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="50 MB",
    retention="7 days",
    compression="zip"
)

def get_logger(name: str):
    """Get a logger instance with the given name"""
    return logger.bind(name=name)
