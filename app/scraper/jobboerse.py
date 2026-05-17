"""
app/scraper/jobboerse.py
Playwright-based scraper for arbeitsagentur.de/jobsuche (Jobbörse).

Design principles:
  - Randomised human-like delays between every action
  - Realistic browser fingerprint (real user-agent, viewport)
  - Pagination support
  - Graceful error handling — one bad job never kills the session
  - Never saves duplicates (checked before touching DB)
"""
import asyncio
import random
import re
from datetime import datetime, timezone
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from app.database.crud import save_job, job_exists
from app.utils.logger import logger
from config.settings import settings

# ── Constants ──────────────────────────────────────────────────────────────────
JOBBOERSE_BASE = "https://www.arbeitsagentur.de/jobsuche/suche"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

async def human_delay(min_s: float = None, max_s: float = None) -> None:
    """Sleep a random amount to mimic human reading/clicking speed."""
    lo = min_s or settings.SCRAPER_DELAY_MIN
    hi = max_s or settings.SCRAPER_DELAY_MAX
    await asyncio.sleep(random.uniform(lo, hi))


async def human_type(page: Page, selector: str, text: str) -> None:
    """Type text character-by-character with human timing."""
    await page.click(selector)
    await asyncio.sleep(random.uniform(0.3, 0.7))
    for char in text:
        await page.keyboard.type(char, delay=random.randint(40, 130))
    await asyncio.sleep(random.uniform(0.4, 1.0))


# ── Browser setup ──────────────────────────────────────────────────────────────

async def create_browser() -> tuple[Browser, BrowserContext]:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=settings.SCRAPER_HEADLESS,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": random.randint(1280, 1440), "height": random.randint(800, 900)},
        locale="de-DE",
        timezone_id="Europe/Berlin",
        extra_http_headers={
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
        },
    )
    # Hide WebDriver flag
    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return browser, context


# ── Job detail extraction ──────────────────────────────────────────────────────

async def extract_job_detail(page: Page, job_url: str) -> Optional[dict]:
    """
    Navigate to a job detail page and extract all available fields.
    Returns None on failure so the caller can skip gracefully.
    """
    try:
        await page.goto(job_url, wait_until="domcontentloaded", timeout=30_000)
        await human_delay(1.5, 3.0)

        # ── Title ──────────────────────────────────────────────────────────────
        title = await _safe_text(page, "h1")

        # ── Company ────────────────────────────────────────────────────────────
        company = await _safe_text(
            page,
            '[data-testid="stellenangebot-arbeitgeber"], .rb-heading--company, h2'
        )

        # ── Location ───────────────────────────────────────────────────────────
        location = await _safe_text(
            page,
            '[data-testid="stellenangebot-ort"], .location'
        )

        # ── Posted date ────────────────────────────────────────────────────────
        posted_date = await _safe_text(
            page,
            '[data-testid="stellenangebot-einstellungsdatum"], time'
        )

        # ── Description (full text block) ─────────────────────────────────────
        description_el = await page.query_selector(
            '[data-testid="stellenangebot-beschreibung"], .rb-jobdetail__content, article'
        )
        description = await description_el.inner_text() if description_el else ""

        # ── Contact info — sometimes in a dedicated section ────────────────────
        contact_name = await _safe_text(page, '[data-testid="contact-name"], .contact__name')
        contact_email = _extract_email(description) or await _safe_text(
            page, '[data-testid="contact-email"], a[href^="mailto:"]'
        )
        if contact_email and contact_email.startswith("mailto:"):
            contact_email = contact_email[7:]

        # ── Raw HTML for future re-parsing ─────────────────────────────────────
        raw_html = await page.content()

        return {
            "title": title or "Unbekannte Stelle",
            "company": company or "Unbekanntes Unternehmen",
            "location": location,
            "job_url": job_url,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "description": description.strip(),
            "raw_html": raw_html[:50_000],  # cap to avoid giant rows
            "posted_date": posted_date,
            "source": "jobboerse",
        }

    except Exception as exc:
        logger.error(f"Failed to extract detail from {job_url}: {exc}")
        return None


async def _safe_text(page: Page, selector: str) -> str:
    """Return inner text of first matching element, or empty string."""
    try:
        el = await page.query_selector(selector)
        return (await el.inner_text()).strip() if el else ""
    except Exception:
        return ""


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text, re.IGNORECASE)
    return match.group(0) if match else None


# ── Search + pagination ────────────────────────────────────────────────────────

async def get_job_links_from_results(page: Page) -> list[str]:
    """Collect all job detail URLs from the current results page."""
    await page.wait_for_selector(
        '[data-testid="jobcard-link"], a.jobtitle, .ergebnis-liste a',
        timeout=15_000,
    )
    elements = await page.query_selector_all(
        '[data-testid="jobcard-link"], a.jobtitle, .ergebnis-liste a'
    )
    links = []
    for el in elements:
        href = await el.get_attribute("href")
        if href:
            if href.startswith("/"):
                href = "https://www.arbeitsagentur.de" + href
            links.append(href)
    return list(dict.fromkeys(links))  # deduplicate while preserving order


async def go_to_next_page(page: Page) -> bool:
    """Click the 'next page' button. Returns False if no next page."""
    try:
        next_btn = await page.query_selector(
            '[data-testid="pagination-next"], button[aria-label="Nächste Seite"], .pagination__next'
        )
        if not next_btn:
            return False
        is_disabled = await next_btn.get_attribute("disabled")
        if is_disabled:
            return False
        await next_btn.click()
        await human_delay(2.0, 4.0)
        return True
    except Exception as exc:
        logger.debug(f"Pagination ended or error: {exc}")
        return False


# ── Main scraper entry point ───────────────────────────────────────────────────

async def scrape_jobs(
    keywords: str,
    location: str = "",
    max_pages: int = 5,
    max_jobs: int = 50,
) -> int:
    """
    Full scrape run:
      1. Open Jobbörse
      2. Search by keywords + optional location
      3. Paginate up to max_pages
      4. Visit each job detail page
      5. Save new jobs to DB

    Returns the number of newly saved jobs.
    """
    logger.info(f"Starting scrape — keywords='{keywords}' location='{location}'")
    browser, context = await create_browser()
    page = await context.new_page()
    saved_count = 0

    try:
        # ── Step 1: Navigate ───────────────────────────────────────────────────
        await page.goto(JOBBOERSE_BASE, wait_until="domcontentloaded", timeout=30_000)
        await human_delay(2.0, 4.0)

        # ── Step 2: Accept cookies if banner appears ───────────────────────────
        try:
            cookie_btn = await page.wait_for_selector(
                'button:has-text("Alle akzeptieren"), button:has-text("Zustimmen"), #ba-button-accept-all-of-them',
                timeout=5_000,
            )
            if cookie_btn:
                await cookie_btn.click()
                await human_delay(1.0, 2.0)
                logger.debug("Cookie banner accepted.")
        except Exception:
            pass  # No banner — that's fine

        # ── Step 3: Fill search form ───────────────────────────────────────────
        await human_type(
            page,
            'input[data-testid="suche-berufsbezeichnung-was"], input[placeholder*="Jobtitel"], input[name="was"]',
            keywords,
        )
        if location:
            await human_type(
                page,
                'input[data-testid="suche-ort-wo"], input[placeholder*="Arbeitsort"], input[name="wo"]',
                location,
            )

        await page.keyboard.press("Enter")
        await human_delay(2.5, 5.0)

        # ── Step 4: Paginate and collect links ────────────────────────────────
        all_links: list[str] = []
        for page_num in range(1, max_pages + 1):
            logger.info(f"Reading results page {page_num}…")
            try:
                links = await get_job_links_from_results(page)
                logger.info(f"  Found {len(links)} links on page {page_num}")
                all_links.extend(links)
                if len(all_links) >= max_jobs:
                    break
                has_next = await go_to_next_page(page)
                if not has_next:
                    logger.info("No more pages.")
                    break
            except Exception as exc:
                logger.warning(f"Page {page_num} failed: {exc}")
                break

        all_links = list(dict.fromkeys(all_links))[:max_jobs]
        logger.info(f"Total unique links to process: {len(all_links)}")

        # ── Step 5: Visit each detail page ────────────────────────────────────
        for i, url in enumerate(all_links, 1):
            if job_exists(url):
                logger.debug(f"[{i}/{len(all_links)}] Already in DB, skipping.")
                continue

            logger.info(f"[{i}/{len(all_links)}] Scraping: {url}")
            detail = await extract_job_detail(page, url)
            if detail:
                save_job(detail)
                saved_count += 1
            await human_delay()  # respect the site between jobs

    except Exception as exc:
        logger.error(f"Scraper crashed: {exc}", exc_info=True)
    finally:
        await browser.close()

    logger.info(f"Scrape complete. Saved {saved_count} new jobs.")
    return saved_count


# ── CLI convenience ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "Python Entwickler"
    loc = sys.argv[2] if len(sys.argv) > 2 else "Berlin"
    asyncio.run(scrape_jobs(kw, loc, max_pages=3, max_jobs=20))
