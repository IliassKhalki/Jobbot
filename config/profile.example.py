"""
config/profile.py
Your personal candidate profile.
Edit the values below — this is what the AI uses to write your Bewerbungen.
"""

CANDIDATE_PROFILE = {
    # ── Personal ───────────────────────────────────────────────────────────────
    "full_name": "Iliass Khalki",
    "email": "iliass.khalki@gmail.com",
    "phone": "(+212) 7 78 47 29 65",
    "address": "X",
    "nationality": "Deutsch-Marokkanisch",
    "linkedin": "https://linkedin.com/in/iliasskhalki",
    "github": "https://github.com/iliasskhalki",
    ##"portfolio": "https://iliasskhalki.dev",
    # ── Languages ──────────────────────────────────────────────────────────────
    "languages": [
        {"language": "Arabisch", "level": "Muttersprache"},
        {"language": "Englisch", "level": "Fließend"},
        {"language": "Französisch", "level": "fließend"},
        {"language": "Deutsch", "level": "Mittelstufe (B2)"},
        {"language": "Russisch", "level": "Grundkenntnisse "},
    ],
    # ── Technical Skills ───────────────────────────────────────────────────────
    "skills": [
        [
            "Python",
            "Flask",
            "FastAPI",
            "JavaScript",
            "React",
            "Node.js",
            "SQLite",
            "Express.js",
            "Firebase",
            "Kotlin",
            "Jetpack Compose",
            "TailwindCSS",
            "Github",
            "Docker",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Docker",
            "Git",
            "Linux",
            "REST APIs",
            "OpenAI API",
            "Playwright",
            "Web Scraping",
            "API Integration",
            "Chart.js",
            "HTML",
            "CSS",
            "Discord Bot Development",
        ]
    ],
    # ── Experience ─────────────────────────────────────────────────────────────
    "experience": [
        {
            "title": "Junior Full-Stack-Entwickler",
            "company": "Evead Group",
            "location": "Casablanca, Marokko",
            "start": "2023-11",
            "end": "2024-05",
            "description": (
                "Konzeption und Implementierung von Frontend- und Backend-Komponenten. "
                "Integration sicherer Funktionen für Video-Upload und -Streaming. "
                "Deployment mit Docker und Nginx. "
                "Anwendung von Clean-Code-Prinzipien und Unit-Tests."
            ),
        },
        {
            "title": "Junior Mobile Entwickler",
            "company": "Ibn Tofail Universität",
            "location": "Kenitra, Marokko",
            "start": "2023-02",
            "end": "2023-07",
            "description": (
                "Entwicklung einer Android-Mobilanwendung für die Studentendiensteabteilung. "
                "UI-Mockup-Design mit Jetpack Compose und Kotlin. "
                "Zusammenarbeit im Team zur Lösung technischer Probleme."
            ),
        },
        {
            "title": "IT-Assistent Techniker",
            "company": "Ibn Tofail Universität",
            "location": "Kenitra, Marokko",
            "start": "2022-12",
            "end": "2023-01",
            "description": (
                "Unterstützung bei LAN/WAN-Netzwerkgestaltung und -implementierung. "
                "Installation und Konfiguration von Servern, Routern und Switches. "
                "Wartung von Computerhardware und Bearbeitung von Support-Tickets."
            ),
        },
    ],
    # ── Education ──────────────────────────────────────────────────────────────
    "education": [
        {
            "degree": "B.Sc. Informatik",
            "institution": "Nationale Universität – Yuri Kondratyuk Poltava Polytechnic",
            "graduation": "2022",
        },
        {
            "degree": "Bakkalaureat in Elektrotechnologie-Wissenschaften",
            "institution": "Moulay Ismail Gymnasium",
            "graduation": "2018",
        },
    ],
    # ── Key Projects ───────────────────────────────────────────────────────────
    "projects": [
        {
            "name": "Video-Streaming Webanwendung",
            "description": "Webanwendung zum Hochladen und Ansehen von Videos mit integrierter lokaler Werbung, optimiert für die Nutzung während des Transports.",
            "tech": ["ReactJS", "NodeJS", "ExpressJS", "Docker"],
            "url": "",
        },
        {
            "name": "Android Studentenservice-App",
            "description": "Native Android-App für die Studentendiensteabteilung zur Verbesserung der Kommunikation und Bereitstellung von Campus-Ressourcen.",
            "tech": ["Kotlin", "Jetpack Compose", "Firebase", "XML"],
            "url": "",
        },
        {
            "name": "Pizzeria Mobile App & Website",
            "description": "Mobile Anwendung und Website für eine Pizzeria.",
            "tech": ["Jetpack Compose", "Kotlin", "JavaScript", "HTML/CSS"],
            "url": "",
        },
        {
            "name": "Spotify Listening Tracker",
            "description": "Full-Stack Webanwendung zur Verfolgung und Visualisierung von Spotify-Hördaten. Nutzer können sich mit ihrem Spotify-Konto anmelden, ihre Hörhistorie analysieren und Daten in interaktiven Charts visualisieren.",
            "tech": [
                "Python",
                "Flask",
                "SQLite",
                "Chart.js",
                "HTML/CSS",
                "JavaScript",
                "Spotify API",
                "OAuth2",
            ],
            "url": "",
        },
    ],
    # ── Certificates ───────────────────────────────────────────────────────────
    "certificates": [
        {"name": "Zertifikat ZB1 OSB B1", "year": 2026},
        {"name": "Computer Science Bachelor Diplom", "year": 2022},
    ],
    # ── Preferences ────────────────────────────────────────────────────────────
    "desired_salary": "42.000 – 60.000 EUR brutto/Jahr",
    "availability": "Ab sofort",
    "work_modes": ["Onsite"],
}
