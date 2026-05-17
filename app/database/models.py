"""
app/database/models.py
SQLAlchemy ORM models for JobBot.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from config.settings import settings


class Base(DeclarativeBase):
    pass


class Job(Base):
    """A scraped job listing."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Core fields ────────────────────────────────────────────────────────────
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    job_url = Column(String(1024), unique=True, nullable=False)  # dedup key
    source = Column(String(64), default="jobboerse")  # future: linkedin, stepstone…

    # ── Contact ────────────────────────────────────────────────────────────────
    contact_name = Column(String(255))
    contact_email = Column(String(255))

    # ── Content ────────────────────────────────────────────────────────────────
    description = Column(Text)
    raw_html = Column(Text)          # full page HTML for re-parsing later

    # ── Meta ───────────────────────────────────────────────────────────────────
    posted_date = Column(String(64))
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Workflow status ────────────────────────────────────────────────────────
    # pending | applied | rejected | interview | ignored
    status = Column(String(32), default="pending")

    # ── Relationships ──────────────────────────────────────────────────────────
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title!r} company={self.company!r}>"


class Application(Base):
    """A generated (and possibly sent) Bewerbung for a job."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # ── Generated content ──────────────────────────────────────────────────────
    email_subject = Column(String(512))
    email_body = Column(Text)
    cover_letter = Column(Text)
    generation_prompt = Column(Text)     # full prompt used — for debugging
    ai_model = Column(String(64))

    # ── Edits ──────────────────────────────────────────────────────────────────
    edited_subject = Column(String(512))  # user's manual edits
    edited_body = Column(Text)
    edited_cover = Column(Text)

    # ── Attachments ────────────────────────────────────────────────────────────
    attachments = Column(JSON, default=list)   # list of file paths

    # ── State ──────────────────────────────────────────────────────────────────
    approved = Column(Boolean, default=False)  # user clicked "approve"
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relationships ──────────────────────────────────────────────────────────
    job = relationship("Job", back_populates="applications")

    @property
    def final_subject(self) -> str:
        """Return edited subject if available, else generated."""
        return self.edited_subject or self.email_subject or ""

    @property
    def final_body(self) -> str:
        return self.edited_body or self.email_body or ""

    @property
    def final_cover(self) -> str:
        return self.edited_cover or self.cover_letter or ""

    def __repr__(self) -> str:
        return f"<Application id={self.id} job_id={self.job_id} sent={self.sent}>"


# ── Engine / session factory ───────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=False,
)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Return a new SQLAlchemy session. Caller must close it."""
    return Session(engine)
