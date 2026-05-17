"""
app/ai/generator.py
Generates personalised German Bewerbung emails and cover letters using OpenAI.

Design principles:
  - System prompt enforces authentic German business writing
  - Job description + candidate profile are injected as context
  - Relevant projects are selected automatically
  - Returns structured output (subject, body, cover letter)
"""
import json
from dataclasses import dataclass
from openai import OpenAI
from app.utils.logger import logger
from config.settings import settings
from config.profile import CANDIDATE_PROFILE

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@dataclass
class GeneratedApplication:
    email_subject: str
    email_body: str
    cover_letter: str
    prompt_used: str
    model: str


# ── Project selector ───────────────────────────────────────────────────────────

def _select_relevant_projects(job_description: str, n: int = 2) -> list[dict]:
    """
    Pick the candidate's most relevant projects based on keyword overlap
    with the job description. Simple TF overlap — no external API needed.
    """
    desc_lower = job_description.lower()
    scored = []
    for proj in CANDIDATE_PROFILE.get("projects", []):
        score = sum(
            1 for tech in proj.get("tech", [])
            if tech.lower() in desc_lower
        )
        scored.append((score, proj))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:n]]


# ── Prompt builder ─────────────────────────────────────────────────────────────

def _build_prompt(job: dict) -> str:
    profile = CANDIDATE_PROFILE
    projects = _select_relevant_projects(job.get("description", ""))

    projects_text = "\n".join(
        f"  - {p['name']}: {p['description']} (Tech: {', '.join(p['tech'])})"
        for p in projects
    ) or "  Keine besonders relevanten Projekte ausgewählt."

    skills_text = ", ".join(profile.get("skills", []))
    experience_text = "\n".join(
        f"  - {e['title']} @ {e['company']} ({e['start']} – {e['end']}): {e['description']}"
        for e in profile.get("experience", [])
    )

    prompt = f"""Du bist ein erfahrener Karrierecoach und Bewerbungsexperte für den deutschsprachigen Arbeitsmarkt.

## Deine Aufgabe
Schreibe eine professionelle, authentische Bewerbung auf Deutsch für die unten beschriebene Stelle.

## Regeln
- Schreibe auf Deutsch (Hochdeutsch, keine Dialekte)
- Klinge wie ein echter Mensch, nicht wie eine KI
- Vermeide Klischees wie „hiermit bewerbe ich mich" oder „mit freundlichen Grüßen" als einzigen Abschluss
- Sei konkret — erwähne echte Technologien aus der Stellenausschreibung
- Halte die E-Mail unter 250 Wörter (prägnant = professionell)
- Das Anschreiben darf länger sein (max. 400 Wörter)
- Hebe 1-2 relevante Projekte des Bewerbers hervor

## Kandidat
- Name: {profile['full_name']}
- E-Mail: {profile['email']}
- Telefon: {profile['phone']}
- Adresse: {profile['address']}
- Sprachen: {', '.join(f"{l['language']} ({l['level']})" for l in profile['languages'])}
- Skills: {skills_text}
- Verfügbarkeit: {profile.get('availability', 'Ab sofort')}
- Gehaltsvorstellung: {profile.get('desired_salary', 'nach Vereinbarung')}

## Berufserfahrung
{experience_text}

## Relevante Projekte für diese Stelle
{projects_text}

## Stellenanzeige
- **Titel**: {job.get('title', 'Nicht angegeben')}
- **Unternehmen**: {job.get('company', 'Nicht angegeben')}
- **Ort**: {job.get('location', 'Nicht angegeben')}
- **Ansprechpartner**: {job.get('contact_name') or 'Nicht angegeben'}
- **Stellenbeschreibung**:
{job.get('description', 'Keine Beschreibung verfügbar.')[:3000]}

## Output Format (JSON — nichts anderes!)
Antworte NUR mit diesem JSON-Objekt:
{{
  "email_subject": "...",
  "email_body": "...",
  "cover_letter": "..."
}}

email_subject: kurze, professionelle Betreffzeile
email_body: kurze Bewerbungs-E-Mail (Fließtext, kein HTML)
cover_letter: formelles Anschreiben mit Datum, Adressblock, Betreff, Brieftext
"""
    return prompt


# ── Main generator function ────────────────────────────────────────────────────

def generate_application(job: dict) -> GeneratedApplication:
    """
    Generate a Bewerbung for the given job dict.
    job must have at minimum: title, company, description
    Raises on API failure.
    """
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in .env")

    prompt = _build_prompt(job)
    logger.info(f"Generating Bewerbung for: {job.get('title')} @ {job.get('company')}")

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Du bist ein Experte für deutsche Bewerbungsschreiben. "
                    "Antworte immer nur mit einem validen JSON-Objekt ohne Markdown-Formatierung."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    logger.debug(f"OpenAI raw response: {raw[:200]}…")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse OpenAI JSON: {exc}\nRaw: {raw}")
        raise

    return GeneratedApplication(
        email_subject=data.get("email_subject", ""),
        email_body=data.get("email_body", ""),
        cover_letter=data.get("cover_letter", ""),
        prompt_used=prompt,
        model=settings.OPENAI_MODEL,
    )
