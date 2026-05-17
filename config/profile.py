"""
config/profile.py
Your personal candidate profile.
Edit the values below — this is what the AI uses to write your Bewerbungen.
"""

CANDIDATE_PROFILE = {
    # ── Personal ───────────────────────────────────────────────────────────────
    "full_name": "Max Mustermann",
    "email": "max@example.com",
    "phone": "+49 170 1234567",
    "address": "Musterstraße 1, 10115 Berlin, Deutschland",
    "nationality": "Deutsch",
    "linkedin": "https://linkedin.com/in/maxmustermann",
    "github": "https://github.com/maxmustermann",
    "portfolio": "https://maxmustermann.dev",

    # ── Languages ──────────────────────────────────────────────────────────────
    "languages": [
        {"language": "Deutsch", "level": "Muttersprache"},
        {"language": "Englisch", "level": "Fließend (C1)"},
        {"language": "Arabisch", "level": "Grundkenntnisse (A2)"},
    ],

    # ── Technical Skills ───────────────────────────────────────────────────────
    "skills": [
        "Python", "FastAPI", "Flask", "Django",
        "JavaScript", "TypeScript", "React", "Node.js",
        "PostgreSQL", "MySQL", "SQLite", "Redis",
        "Docker", "Git", "Linux", "REST APIs",
        "Machine Learning", "OpenAI API", "Playwright",
    ],

    # ── Experience ─────────────────────────────────────────────────────────────
    "experience": [
        {
            "title": "Backend Developer",
            "company": "Tech GmbH",
            "location": "Berlin",
            "start": "2022-01",
            "end": "present",
            "description": (
                "Entwicklung von REST APIs mit FastAPI und Python. "
                "Datenbankdesign mit PostgreSQL. "
                "Containerisierung mit Docker. "
                "Code Reviews und agile Arbeitsweise in einem 5-köpfigen Team."
            ),
        },
        {
            "title": "Junior Developer",
            "company": "Startup XYZ",
            "location": "Hamburg",
            "start": "2020-06",
            "end": "2021-12",
            "description": (
                "Webentwicklung mit Django und React. "
                "Integration von Drittanbieter-APIs. "
                "Technische Dokumentation auf Deutsch und Englisch."
            ),
        },
    ],

    # ── Education ──────────────────────────────────────────────────────────────
    "education": [
        {
            "degree": "B.Sc. Informatik",
            "institution": "Technische Universität Berlin",
            "graduation": "2020",
        }
    ],

    # ── Key Projects (referenced by AI generator) ─────────────────────────────
    "projects": [
        {
            "name": "JobBot",
            "description": "Automatisiertes Bewerbungssystem mit Playwright, OpenAI und Flask.",
            "tech": ["Python", "Playwright", "OpenAI", "Flask", "SQLite"],
            "url": "https://github.com/maxmustermann/jobbot",
        },
        {
            "name": "AI Chat Dashboard",
            "description": "Echtzeit-Chat-Applikation mit GPT-4 Integration und React Frontend.",
            "tech": ["React", "Node.js", "OpenAI", "WebSockets"],
            "url": "https://github.com/maxmustermann/ai-chat",
        },
    ],

    # ── Certificates ───────────────────────────────────────────────────────────
    "certificates": [
        {"name": "AWS Certified Developer", "year": 2023},
        {"name": "Python Institute PCEP", "year": 2021},
    ],

    # ── Preferences ────────────────────────────────────────────────────────────
    "desired_salary": "60.000 – 70.000 EUR brutto/Jahr",
    "availability": "Ab sofort",
    "work_modes": ["Remote", "Hybrid"],
}
