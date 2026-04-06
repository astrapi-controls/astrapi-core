"""core/modules/sysinfo/ui.py – FastAPI-Router für Sysinfo UI-Routen."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi.core.ui.render import render
from .engine import collect

KEY    = "sysinfo"
router = APIRouter()


@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def sysinfo_content(request: Request):
    return render(request, f"{KEY}/partials/tab.html", {"info": collect()})


@router.get(f"/ui/{KEY}/metrics", response_class=HTMLResponse)
def sysinfo_metrics(request: Request):
    return render(request, f"{KEY}/partials/metrics.html", {"info": collect()})
