"""dev_app/modules/demo_log/ui.py – Read-only Beispiel-Log-Liste"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi.core.ui.render import render

KEY    = "demo_log"
router = APIRouter()

_ENTRIES = [
    {"ts": "2026-03-26 10:00:00", "level": "INFO",  "message": "Dienst gestartet"},
    {"ts": "2026-03-26 10:01:15", "level": "INFO",  "message": "Konfiguration geladen (3 Einträge)"},
    {"ts": "2026-03-26 10:05:42", "level": "WARN",  "message": "Verbindung zu Host-02 verzögert"},
    {"ts": "2026-03-26 10:08:01", "level": "ERROR", "message": "Timeout beim Abruf von Host-03"},
    {"ts": "2026-03-26 10:08:45", "level": "INFO",  "message": "Wiederverbindung zu Host-03 erfolgreich"},
    {"ts": "2026-03-26 10:15:00", "level": "INFO",  "message": "Geplanter Job abgeschlossen"},
]


@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def content(request: Request):
    return render(request, f"{KEY}/partials/list.html", {"entries": _ENTRIES})
