"""
app/database/crud.py
Clean data-access functions. All DB logic lives here — never in routes or scraper.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import Job, Application, get_session
from app.utils.logger import logger


# ── Jobs ───────────────────────────────────────────────────────────────────────

def job_exists(url: str) -> bool:
    """Return True if a job with this URL is already in the database."""
    with get_session() as s:
        return s.query(Job).filter_by(job_url=url).first() is not None


def save_job(data: dict) -> Optional[Job]:
    """
    Insert a new job. Returns the Job object, or None if it's a duplicate.
    data keys must match Job columns.
    """
    if job_exists(data.get("job_url", "")):
        logger.debug(f"Skipping duplicate: {data.get('job_url')}")
        return None

    with get_session() as s:
        job = Job(**{k: v for k, v in data.items() if hasattr(Job, k)})
        s.add(job)
        s.commit()
        s.refresh(job)
        logger.info(f"Saved job: {job.title} @ {job.company}")
        return job


def get_jobs(
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Job]:
    """Fetch jobs with optional filters."""
    with get_session() as s:
        q = s.query(Job)
        if status:
            q = q.filter(Job.status == status)
        if search:
            like = f"%{search}%"
            q = q.filter(
                Job.title.ilike(like) |
                Job.company.ilike(like) |
                Job.location.ilike(like) |
                Job.description.ilike(like)
            )
        jobs = q.order_by(Job.scraped_at.desc()).offset(offset).limit(limit).all()
        # Detach from session so we can serialise later
        s.expunge_all()
        return jobs


def get_job(job_id: int) -> Optional[Job]:
    with get_session() as s:
        job = s.get(Job, job_id)
        if job:
            s.expunge(job)
        return job


def update_job_status(job_id: int, status: str) -> bool:
    valid = {"pending", "applied", "rejected", "interview", "ignored"}
    if status not in valid:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
    with get_session() as s:
        job = s.get(Job, job_id)
        if not job:
            return False
        job.status = status
        s.commit()
        return True


# ── Applications ───────────────────────────────────────────────────────────────

def save_application(
    job_id: int,
    email_subject: str,
    email_body: str,
    cover_letter: str,
    prompt: str,
    model: str,
    attachments: list[str],
) -> Application:
    with get_session() as s:
        app = Application(
            job_id=job_id,
            email_subject=email_subject,
            email_body=email_body,
            cover_letter=cover_letter,
            generation_prompt=prompt,
            ai_model=model,
            attachments=attachments,
        )
        s.add(app)
        s.commit()
        s.refresh(app)
        s.expunge(app)
        logger.info(f"Saved application #{app.id} for job #{job_id}")
        return app


def get_application(application_id: int) -> Optional[Application]:
    with get_session() as s:
        app = s.get(Application, application_id)
        if app:
            s.expunge(app)
        return app


def update_application(application_id: int, **fields) -> bool:
    """Update any subset of Application fields."""
    with get_session() as s:
        app = s.get(Application, application_id)
        if not app:
            return False
        for key, value in fields.items():
            if hasattr(app, key):
                setattr(app, key, value)
        s.commit()
        return True


def approve_application(application_id: int) -> bool:
    return update_application(application_id, approved=True)


def mark_sent(application_id: int) -> bool:
    return update_application(
        application_id,
        sent=True,
        sent_at=datetime.now(timezone.utc),
    )
