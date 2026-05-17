"""
config/settings.py
Centralised configuration loaded from environment variables.
Import `settings` anywhere in the app — never import os.environ directly.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # ── Project paths ──────────────────────────────────────────────────────────
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # ── Flask ──────────────────────────────────────────────────────────────────
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'jobbot.db'}")

    # ── OpenAI ─────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # ── Gmail ──────────────────────────────────────────────────────────────────
    GMAIL_ADDRESS: str = os.getenv("GMAIL_ADDRESS", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")

    # ── Scraper ────────────────────────────────────────────────────────────────
    SCRAPER_HEADLESS: bool = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
    SCRAPER_DELAY_MIN: float = float(os.getenv("SCRAPER_DELAY_MIN", 2))
    SCRAPER_DELAY_MAX: float = float(os.getenv("SCRAPER_DELAY_MAX", 5))

    # ── Files ──────────────────────────────────────────────────────────────────
    CV_PATH: Path = BASE_DIR / os.getenv("CV_PATH", "data/cvs/my_cv.pdf")
    CERTIFICATES_DIR: Path = BASE_DIR / os.getenv("CERTIFICATES_DIR", "data/certificates/")

    def validate(self) -> None:
        """Warn about missing critical keys on startup."""
        missing = []
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not self.GMAIL_ADDRESS:
            missing.append("GMAIL_ADDRESS")
        if not self.GMAIL_APP_PASSWORD:
            missing.append("GMAIL_APP_PASSWORD")
        if missing:
            from app.utils.logger import logger
            logger.warning(f"Missing env vars: {', '.join(missing)} — some features disabled.")


settings = Settings()
