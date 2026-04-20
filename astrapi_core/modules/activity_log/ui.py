# core/modules/activity_log/ui.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi_core.ui.render import render
from .engine import KEY, list_activity, enrich, registered_modules

router = APIRouter()


def _render_content(request) -> str:
    from astrapi_core.ui.render import render_string
    entries = enrich(list_activity(limit=200))
    return render_string(request, "activity_log/content.html", dict(
        container_id="tab-activity_log",
        entries=entries,
        modules=registered_modules(),
    ))


from astrapi_core.ui.page_factory import register_content_renderer
register_content_renderer(KEY, _render_content)


@router.get(f"/ui/{KEY}/clear-confirm", response_class=HTMLResponse)
def clear_confirm(request: Request):
    return render(request, "partials/confirm_modal.html", dict(
        description="Alle Activity-Log-Einträge",
        verb="löschen",
        confirm_url="/api/activity_log/clear",
        method="delete",
        container_id="tab-activity_log",
        loading_id="activity_log-loading",
    ))


@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def content(request: Request):
    entries = enrich(list_activity(limit=200))
    return render(request, "activity_log/content.html", dict(
        container_id="tab-activity_log",
        entries=entries,
        modules=registered_modules(),
    ))
