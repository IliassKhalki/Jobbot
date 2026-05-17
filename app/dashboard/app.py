"""
app/dashboard/app.py
Flask application factory.
"""
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.dashboard.routes import api
from app.database.models import init_db
from app.utils.logger import logger
from config.settings import settings

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
    app.secret_key = settings.FLASK_SECRET_KEY
    CORS(app)

    # Register API blueprint
    app.register_blueprint(api)

    # Serve the SPA index for all non-API routes
    @app.get("/")
    def index():
        return send_from_directory(str(TEMPLATE_DIR), "index.html")

    # Initialise database
    init_db()
    logger.info("Database initialised.")

    settings.validate()
    return app
