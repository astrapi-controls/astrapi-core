"""
astrapi-flask-ui V3 – Einstiegspunkt (FastAPI + Flask)

FastAPI  → /api/...       JSON-Endpunkte, OpenAPI, Swagger
Flask    → /              UI, HTMX-Partials, Modals
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
APP_ROOT     = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from a2wsgi import WSGIMiddleware

from core.ui import create as create_ui
from app.api.fastapi_app import create as create_api


def create_app() -> FastAPI:
    api = create_api()
    ui  = create_ui(app_root=APP_ROOT)

    core_static = PROJECT_ROOT / "core" / "static"
    api.mount("/static", StaticFiles(directory=str(core_static)), name="static")
    api.mount("/", WSGIMiddleware(ui))

    return api


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
