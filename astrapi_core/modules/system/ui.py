"""core/modules/system/ui.py – FastAPI-Router für System-UI (Sysinfo + Updater)."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi_core.ui.render import render
from .engine import collect
from . import updater as _updater

KEY    = "system"
router = APIRouter()


def _render_content(request) -> str:
    from astrapi_core.ui.render import render_string
    return render_string(request, f"{KEY}/content.html", {"container_id": f"tab-{KEY}", "info": collect()})


from astrapi_core.ui.page_factory import register_content_renderer
register_content_renderer(KEY, _render_content)


@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def system_content(request: Request):
    return render(request, f"{KEY}/content.html", {"container_id": f"tab-{KEY}", "info": collect()})


@router.get(f"/ui/{KEY}/metrics", response_class=HTMLResponse)
def system_metrics(request: Request):
    return render(request, f"{KEY}/partials/metrics.html", {"info": collect()})


@router.post(f"/ui/{KEY}/check", response_class=HTMLResponse)
def system_check(request: Request):
    _updater.check_updates()
    return render(request, f"{KEY}/partials/metrics.html", {"info": collect()})


@router.post(f"/ui/{KEY}/update", response_class=HTMLResponse)
def system_update(request: Request):
    _updater.run_update()
    return render(request, f"{KEY}/modals/update.html", _log_ctx())


@router.get(f"/ui/{KEY}/update-log", response_class=HTMLResponse)
def system_update_log(request: Request):
    return render(request, f"{KEY}/partials/update_log.html", _log_ctx())


def _log_ctx() -> dict:
    st = _updater.get_status()
    return {
        "status":  st["status"],
        "output":  st["output"],
        "error":   st["error"],
        "log_id":  st["log_id"],
    }
