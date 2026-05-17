"""
app/email/sender.py
Send Bewerbung emails via Gmail SMTP with PDF attachments.

Security:
  - Credentials come from .env only
  - Never hardcoded

Usage:
  from app.email.sender import send_application
  send_application(application_id=5)
"""
import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from app.database.crud import get_application, get_job, mark_sent, update_job_status
from app.utils.logger import logger
from config.settings import settings
from config.profile import CANDIDATE_PROFILE


def _build_message(
    to_email: str,
    subject: str,
    body: str,
    attachments: list[str],
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = f"{CANDIDATE_PROFILE['full_name']} <{settings.GMAIL_ADDRESS}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    for path_str in attachments:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Attachment not found, skipping: {path}")
            continue
        mime_type, _ = mimetypes.guess_type(str(path))
        main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=main_type,
                subtype=sub_type,
                filename=path.name,
            )
        logger.debug(f"Attached: {path.name}")

    return msg


def send_application(application_id: int) -> bool:
    """
    Send a previously approved application by its DB ID.
    Returns True on success, False on failure.
    Raises ValueError if not approved yet.
    """
    app = get_application(application_id)
    if not app:
        raise ValueError(f"Application #{application_id} not found.")
    if not app.approved:
        raise ValueError(f"Application #{application_id} is not approved. Approve it first!")
    if app.sent:
        logger.warning(f"Application #{application_id} already sent — skipping.")
        return False

    job = get_job(app.job_id)
    if not job:
        raise ValueError(f"Job #{app.job_id} not found.")

    to_email = job.contact_email
    if not to_email:
        raise ValueError(f"No contact email for job #{job.id} ({job.title} @ {job.company})")

    if not settings.GMAIL_ADDRESS or not settings.GMAIL_APP_PASSWORD:
        raise RuntimeError("Gmail credentials missing — set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")

    subject = app.final_subject
    body = app.final_body

    # Default attachments: CV + any configured certificates
    attachment_paths: list[str] = list(app.attachments or [])
    if settings.CV_PATH.exists() and str(settings.CV_PATH) not in attachment_paths:
        attachment_paths.insert(0, str(settings.CV_PATH))

    cert_dir = settings.CERTIFICATES_DIR
    if cert_dir.exists():
        for pdf in sorted(cert_dir.glob("*.pdf")):
            if str(pdf) not in attachment_paths:
                attachment_paths.append(str(pdf))

    msg = _build_message(to_email, subject, body, attachment_paths)

    try:
        logger.info(f"Sending to {to_email} — '{subject}'")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.GMAIL_ADDRESS, settings.GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        mark_sent(application_id)
        update_job_status(job.id, "applied")
        logger.info(f"✓ Sent application #{application_id} successfully.")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail authentication failed. Check GMAIL_APP_PASSWORD in .env")
        raise
    except Exception as exc:
        logger.error(f"Failed to send email: {exc}", exc_info=True)
        return False


def send_test_email(to_email: str) -> bool:
    """Send a quick test email to verify SMTP credentials work."""
    msg = EmailMessage()
    msg["From"] = settings.GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = "[JobBot] Test E-Mail"
    msg.set_content("JobBot SMTP-Verbindung funktioniert korrekt!")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.GMAIL_ADDRESS, settings.GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Test email sent to {to_email}")
        return True
    except Exception as exc:
        logger.error(f"Test email failed: {exc}")
        return False
