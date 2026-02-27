"""
AstrapiFlaskUi – Einstiegspunkt

Starten:
    python main.py
    # oder via gunicorn:
    gunicorn "main:app"
"""
from pathlib import Path
from core.ui import create

APP_ROOT = Path(__file__).resolve().parent / "app"

app = create(app_root=APP_ROOT)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
