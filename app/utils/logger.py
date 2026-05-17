"""
app/utils/logger.py
Centralised logger using loguru.
Import `logger` anywhere: from app.utils.logger import logger
"""
import sys
from pathlib import Path
from loguru import logger

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Remove default sink, add our own
logger.remove()

# Console — colourful, readable
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — {message}",
    level="INFO",
    colorize=True,
)

# File — full detail, rotate daily, keep 14 days
logger.add(
    LOG_DIR / "jobbot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} — {message}",
    level="DEBUG",
    rotation="00:00",
    retention="14 days",
    compression="zip",
)
