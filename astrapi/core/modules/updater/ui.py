# core/modules/updater/ui.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi.core.ui.render import render
from . import engine

KEY    = "updater"
router = APIRouter()


def _ctx() -> dict:
    status = engine.get_status()
    return {
        "packages":     status["packages"] or engine.get_packages_with_versions(),
        "status":       status["status"],
        "last_checked": status["last_checked"],
        "output":       status["output"],
        "error":        status["error"],
        "log_id":       status["log_id"],
    }


@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def updater_content(request: Request):
    return render(request, f"{KEY}/partials/tab.html", _ctx())


@router.get(f"/ui/{KEY}/panel", response_class=HTMLResponse)
def updater_panel(request: Request):
    """Nur das Update-Panel – wird per HTMX-Polling aktualisiert."""
    return render(request, f"{KEY}/partials/panel.html", _ctx())


@router.post(f"/ui/{KEY}/check", response_class=HTMLResponse)
def updater_check(request: Request):
    """Führt den Versionscheck synchron durch und rendert das aktualisierte Panel."""
    engine.check_updates()
    return render(request, f"{KEY}/partials/panel.html", _ctx())


@router.post(f"/ui/{KEY}/update", response_class=HTMLResponse)
def updater_update(request: Request):
    """Startet das Update (async) und gibt das Panel mit Polling zurück."""
    engine.run_update()
    return render(request, f"{KEY}/partials/panel.html", _ctx())
