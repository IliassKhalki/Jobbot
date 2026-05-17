"""
run.py
Start the JobBot local server.

Usage:
  python run.py
  python run.py --port 8080

Then open: http://localhost:5000
"""
import argparse
import webbrowser
import threading
import time
from app.dashboard.app import create_app
from app.utils.logger import logger
from config.settings import settings


def open_browser(port: int) -> None:
    """Open the dashboard in the default browser after a short delay."""
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")


def main() -> None:
    parser = argparse.ArgumentParser(description="JobBot — lokaler Bewerbungsmanager")
    parser.add_argument("--port", type=int, default=settings.FLASK_PORT)
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    app = create_app()

    logger.info(f"Starting JobBot on http://localhost:{args.port}")

    if not args.no_browser:
        threading.Thread(target=open_browser, args=(args.port,), daemon=True).start()

    app.run(
        host="127.0.0.1",
        port=args.port,
        debug=settings.FLASK_DEBUG,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
