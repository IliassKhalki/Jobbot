"""
app/dashboard/routes.py
Flask API routes powering the local dashboard.
All endpoints return JSON; the frontend is a single-page HTML app.
"""
import asyncio
from flask import Blueprint, jsonify, request, abort
from app.database.crud import (
    get_jobs, get_job, update_job_status,
    save_application, get_application, update_application,
    approve_application,
)
from app.database.models import Job
from app.ai.generator import generate_application
from app.email.sender import send_application, send_test_email
from app.utils.logger import logger
from config.settings import settings

api = Blueprint("api", __name__, url_prefix="/api")


def _job_to_dict(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_url": job.job_url,
        "contact_name": job.contact_name,
        "contact_email": job.contact_email,
        "description": job.description,
        "posted_date": job.posted_date,
        "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None,
        "status": job.status,
    }


# ── Jobs ───────────────────────────────────────────────────────────────────────

@api.get("/jobs")
def list_jobs():
    status = request.args.get("status")
    search = request.args.get("search")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    jobs = get_jobs(status=status, search=search, limit=limit, offset=offset)
    return jsonify([_job_to_dict(j) for j in jobs])


@api.get("/jobs/<int:job_id>")
def get_job_detail(job_id: int):
    job = get_job(job_id)
    if not job:
        abort(404, description="Job not found")
    return jsonify(_job_to_dict(job))


@api.patch("/jobs/<int:job_id>/status")
def set_job_status(job_id: int):
    body = request.get_json(force=True)
    status = body.get("status")
    if not status:
        abort(400, description="'status' field required")
    try:
        ok = update_job_status(job_id, status)
    except ValueError as e:
        abort(400, description=str(e))
    if not ok:
        abort(404, description="Job not found")
    return jsonify({"ok": True, "status": status})


# ── Scraper ────────────────────────────────────────────────────────────────────

@api.post("/scraper/run")
def run_scraper():
    """
    Start a scrape run in the background.
    Body: { "keywords": "Python", "location": "Berlin", "max_pages": 3 }
    """
    from app.scraper.jobboerse import scrape_jobs

    body = request.get_json(force=True)
    keywords = body.get("keywords", "Python Entwickler")
    location = body.get("location", "")
    max_pages = int(body.get("max_pages", 3))
    max_jobs = int(body.get("max_jobs", 30))

    # Run synchronously for simplicity (Flask dev server is single-threaded)
    # For production, swap to Celery or a background thread
    try:
        saved = asyncio.run(scrape_jobs(keywords, location, max_pages, max_jobs))
        return jsonify({"ok": True, "saved": saved})
    except Exception as exc:
        logger.error(f"Scraper error: {exc}", exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── AI Generator ───────────────────────────────────────────────────────────────

@api.post("/jobs/<int:job_id>/generate")
def generate(job_id: int):
    """Generate a Bewerbung for a job. Returns the new application object."""
    job = get_job(job_id)
    if not job:
        abort(404, description="Job not found")

    try:
        result = generate_application(_job_to_dict(job))
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503
    except Exception as exc:
        logger.error(f"Generation failed: {exc}", exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500

    app_obj = save_application(
        job_id=job_id,
        email_subject=result.email_subject,
        email_body=result.email_body,
        cover_letter=result.cover_letter,
        prompt=result.prompt_used,
        model=result.model,
        attachments=[],
    )

    return jsonify({
        "ok": True,
        "application_id": app_obj.id,
        "email_subject": result.email_subject,
        "email_body": result.email_body,
        "cover_letter": result.cover_letter,
    })


# ── Applications ───────────────────────────────────────────────────────────────

@api.get("/applications/<int:app_id>")
def get_app(app_id: int):
    app_obj = get_application(app_id)
    if not app_obj:
        abort(404)
    return jsonify({
        "id": app_obj.id,
        "job_id": app_obj.job_id,
        "email_subject": app_obj.final_subject,
        "email_body": app_obj.final_body,
        "cover_letter": app_obj.final_cover,
        "approved": app_obj.approved,
        "sent": app_obj.sent,
        "sent_at": app_obj.sent_at.isoformat() if app_obj.sent_at else None,
    })


@api.patch("/applications/<int:app_id>")
def edit_application(app_id: int):
    """Save manual edits."""
    body = request.get_json(force=True)
    allowed = {"edited_subject", "edited_body", "edited_cover"}
    updates = {k: v for k, v in body.items() if k in allowed}
    ok = update_application(app_id, **updates)
    if not ok:
        abort(404)
    return jsonify({"ok": True})


@api.post("/applications/<int:app_id>/approve")
def approve(app_id: int):
    ok = approve_application(app_id)
    if not ok:
        abort(404)
    return jsonify({"ok": True, "approved": True})


@api.post("/applications/<int:app_id>/send")
def send(app_id: int):
    try:
        ok = send_application(app_id)
        return jsonify({"ok": ok})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503
    except Exception as exc:
        logger.error(f"Send failed: {exc}", exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── Settings / health ──────────────────────────────────────────────────────────

@api.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "gmail_configured": bool(settings.GMAIL_ADDRESS and settings.GMAIL_APP_PASSWORD),
        "cv_exists": settings.CV_PATH.exists(),
    })


@api.post("/email/test")
def test_email():
    body = request.get_json(force=True)
    to = body.get("to", settings.GMAIL_ADDRESS)
    try:
        ok = send_test_email(to)
        return jsonify({"ok": ok})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500
