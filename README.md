# ⚡ JobBot — Lokaler Bewerbungsmanager

Automatisiert deine Job-Suche auf der deutschen Jobbörse.  
Scrapet Stellen → Generiert Bewerbungen mit KI → Lässt dich reviewen → Sendet E-Mails.

> **Nur für den persönlichen Gebrauch.** Kein aggressives Scraping. Respektiert Wartezeiten.

---

## 🗂️ Projektstruktur

```
jobbot/
├── run.py                        # App starten
├── setup.bat                     # Windows-Setup (einmalig)
├── requirements.txt
├── .env.example                  # Kopieren → .env, API-Keys eintragen
│
├── config/
│   ├── settings.py               # Alle Einstellungen (aus .env geladen)
│   └── profile.py                # Dein Bewerberprofil ← HIER DATEN EINTRAGEN
│
├── app/
│   ├── scraper/
│   │   └── jobboerse.py          # Playwright-Scraper für arbeitsagentur.de
│   │
│   ├── ai/
│   │   └── generator.py          # OpenAI Bewerbungsgenerator
│   │
│   ├── email/
│   │   └── sender.py             # Gmail SMTP Versand
│   │
│   ├── database/
│   │   ├── models.py             # SQLAlchemy Modelle (Job, Application)
│   │   └── crud.py               # Alle Datenbankoperationen
│   │
│   ├── dashboard/
│   │   ├── app.py                # Flask App-Factory
│   │   ├── routes.py             # REST API Endpunkte
│   │   └── templates/
│   │       └── index.html        # Single-Page Dashboard (kein Framework nötig)
│   │
│   └── utils/
│       └── logger.py             # Loguru-Logger (Konsole + Datei)
│
├── data/
│   ├── cvs/                      # Lebenslauf hier ablegen (my_cv.pdf)
│   └── certificates/             # Zertifikate hier ablegen (*.pdf)
│
└── logs/                         # Automatisch erstellt
```

---

## 🚀 Installation (Windows)

### Schritt 1: Repository klonen / Ordner anlegen

```cmd
cd Desktop
mkdir jobbot
cd jobbot
```

### Schritt 2: Einmalig Setup ausführen

```cmd
setup.bat
```

Das Skript:
- Erstellt eine virtuelle Python-Umgebung (`venv`)
- Installiert alle Abhängigkeiten
- Installiert Playwright + Chromium
- Erstellt `.env` aus dem Template

### Schritt 3: .env ausfüllen

Öffne `.env` mit einem Texteditor:

```
OPENAI_API_KEY=sk-...          ← Von platform.openai.com
GMAIL_ADDRESS=deine@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx   ← Siehe unten!
```

**Gmail App-Passwort erstellen:**
1. Gehe zu myaccount.google.com → Sicherheit
2. Aktiviere 2-Faktor-Authentifizierung
3. Suche nach „App-Passwörter"
4. Erstelle ein Passwort für „Mail" auf „Windows-Computer"
5. Das 16-stellige Passwort → in `.env` eintragen

### Schritt 4: Dein Profil ausfüllen

Öffne `config/profile.py` und trage **deine echten Daten** ein:
- Name, E-Mail, Telefon, Adresse
- Skills, Erfahrung, Ausbildung
- Projekte (werden von der KI für Bewerbungen ausgewählt)

### Schritt 5: CV ablegen

Kopiere deinen Lebenslauf als PDF nach:
```
data/cvs/my_cv.pdf
```

Optional: Zertifikate nach `data/certificates/*.pdf`

### Schritt 6: Starten

```cmd
venv\Scripts\activate
python run.py
```

Der Browser öffnet sich automatisch auf `http://localhost:5000`.

---

## 📖 Benutzung

### Dashboard
- Übersicht: Gesamtanzahl Jobs, Status-Verteilung
- System-Status: OpenAI, Gmail, CV-Check

### Scraper
1. Klicke auf **Scraper** in der Navigation
2. Trage Stichwörter ein (z.B. `Python Entwickler`)
3. Optional: Ort (z.B. `Berlin`)
4. Klicke **▶ Scrapen**
5. Der Scraper öffnet einen Browser im Hintergrund und speichert Jobs in die DB

### Jobs reviewen
1. Klicke auf **Jobs** → siehst alle gescrapten Stellen
2. Nutze Suche und Filter
3. Klicke auf eine Stelle → Detail-Panel öffnet sich
4. Ändere den Status: `Ausstehend → Ignoriert` für irrelevante Jobs

### Bewerbung generieren
1. Öffne eine Stelle
2. Klicke **✨ Bewerbung mit KI generieren**
3. Die KI liest die Stellenbeschreibung + dein Profil
4. Betreff, E-Mail und Anschreiben werden generiert
5. Bearbeite den Text nach Bedarf
6. Klicke **💾 Änderungen speichern**
7. Klicke **✓ Genehmigen** (Sicherheitssperre!)
8. Klicke **📧 E-Mail senden** → Bestätigungsdialog → versendet

---

## 🔌 REST API Referenz

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/health` | System-Status |
| GET | `/api/jobs` | Jobs auflisten (filter: status, search) |
| GET | `/api/jobs/:id` | Job-Detail |
| PATCH | `/api/jobs/:id/status` | Status ändern |
| POST | `/api/scraper/run` | Scraper starten |
| POST | `/api/jobs/:id/generate` | Bewerbung generieren |
| GET | `/api/applications/:id` | Bewerbung abrufen |
| PATCH | `/api/applications/:id` | Bewerbung bearbeiten |
| POST | `/api/applications/:id/approve` | Genehmigen |
| POST | `/api/applications/:id/send` | E-Mail senden |
| POST | `/api/email/test` | Test-E-Mail |

---

## 🛡️ Anti-Ban Best Practices

Der Scraper ist bereits darauf ausgelegt, menschliches Verhalten zu imitieren:

- **Zufällige Delays**: 2–5 Sekunden zwischen jeder Aktion (konfigurierbar in `.env`)
- **Realer User-Agent**: wechselt zwischen Chrome, Firefox, Safari
- **Deutsches Locale**: `de-DE`, Berlin-Timezone
- **WebDriver-Flag versteckt**: `navigator.webdriver = undefined`
- **Pagination respektiert**: kein paralleles Abrufen

**Empfehlung**: Max. 1–2 Scrape-Läufe pro Tag. Nicht nachts scrapen.

---

## 🔮 Zukünftige Erweiterungen

Die Architektur ist darauf vorbereitet:

- `app/scraper/linkedin.py` — LinkedIn-Scraper
- `app/scraper/stepstone.py` — StepStone-Scraper  
- `app/scraper/xing.py` — XING-Scraper
- Mehrere Bewerberprofile (z.B. für verschiedene Jobbereiche)
- Automatisches Matching-Score (Job ↔ Profil)
- Analytics-Dashboard
- Docker-Deployment

---

## ❗ Troubleshooting

**Scraper findet nichts?**
→ Setze `SCRAPER_HEADLESS=false` in `.env` — du siehst dann den Browser live

**Gmail-Fehler 535?**
→ App-Passwort falsch. Neu generieren unter myaccount.google.com

**OpenAI-Fehler 401?**
→ API-Key prüfen auf platform.openai.com — genug Credits?

**Playwright-Browser fehlt?**
→ `playwright install chromium` nochmal ausführen

---

*Gebaut mit Python, Playwright, Flask, SQLite, OpenAI.*
