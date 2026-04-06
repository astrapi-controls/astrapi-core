"""core/modules/scheduler/ui.py – FastAPI-Router für den Multi-Job Scheduler."""
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi.core.ui.render import render

KEY    = "scheduler"
_C_ID  = f"tab-{KEY}"
_L_ID  = f"{KEY}-loading"
router = APIRouter()


def _list_ctx() -> dict:
    from astrapi.core.modules.scheduler.engine import list_jobs, get_registered_actions
    return {
        "jobs":         list_jobs(),
        "actions":      get_registered_actions(),
        "key":          KEY,
        "container_id": _C_ID,
        "loading_id":   _L_ID,
    }


# ── Liste ──────────────────────────────────────────────────────────────────────

@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def scheduler_content(request: Request):
    return render(request, f"{KEY}/partials/tab.html", _list_ctx())


# ── Modals ─────────────────────────────────────────────────────────────────────

@router.get(f"/ui/{KEY}/job/new", response_class=HTMLResponse)
def scheduler_job_new(request: Request):
    from astrapi.core.modules.scheduler.engine import get_registered_actions
    return render(request, f"{KEY}/partials/job_modal.html", dict(
        job=None,
        actions=get_registered_actions(),
        error=None,
        container_id=request.query_params.get("container_id", _C_ID),
        loading_id=request.query_params.get("loading_id", _L_ID),
    ))


@router.get(f"/ui/{KEY}/job/{{job_id}}/edit", response_class=HTMLResponse)
def scheduler_job_edit(job_id: str, request: Request):
    from astrapi.core.modules.scheduler.engine import get_job, get_registered_actions
    job = get_job(job_id)
    if job is None:
        return HTMLResponse("", status_code=404)
    return render(request, f"{KEY}/partials/job_modal.html", dict(
        job=job,
        actions=get_registered_actions(),
        error=None,
        container_id=request.query_params.get("container_id", _C_ID),
        loading_id=request.query_params.get("loading_id", _L_ID),
    ))


@router.get(f"/ui/{KEY}/job/{{job_id}}/delete", response_class=HTMLResponse)
def scheduler_job_delete_modal(job_id: str, request: Request):
    from astrapi.core.modules.scheduler.engine import get_job
    job = get_job(job_id)
    return render(request, "partials/confirm_modal.html", dict(
        description=job["label"] if job else job_id,
        verb="löschen",
        confirm_url=f"/api/{KEY}/{job_id}",
        method="delete",
        reload_url=f"/ui/{KEY}/content",
        container_id=request.query_params.get("container_id", _C_ID),
        loading_id=request.query_params.get("loading_id", _L_ID),
    ))


@router.get(f"/ui/{KEY}/job/{{job_id}}/toggle", response_class=HTMLResponse)
def scheduler_job_toggle_modal(job_id: str, request: Request):
    from astrapi.core.modules.scheduler.engine import get_job
    job     = get_job(job_id) or {}
    enabled = request.query_params.get("enabled", "True")
    verb    = "deaktivieren" if enabled == "True" else "aktivieren"
    return render(request, "partials/confirm_modal.html", dict(
        description=job.get("label", job_id),
        verb=verb,
        confirm_url=f"/api/{KEY}/{job_id}/toggle",
        method="patch",
        reload_url=f"/ui/{KEY}/content",
        container_id=request.query_params.get("container_id", _C_ID),
        loading_id=request.query_params.get("loading_id", _L_ID),
    ))


# ── Apply-Routen (Form-Submit aus Modal) ───────────────────────────────────────

@router.post(f"/ui/{KEY}/job", response_class=HTMLResponse)
async def scheduler_job_create(request: Request):
    from astrapi.core.modules.scheduler.engine import create_job, get_registered_actions
    form = await request.form()

    label        = form.get("label", "").strip()
    cron         = form.get("cron", "").strip()
    enabled      = "1" in form.getlist("enabled")
    steps        = list(form.getlist("steps"))
    notify_start = "1" in form.getlist("notify_start")
    notify_end   = "1" in form.getlist("notify_end")

    if not label or not cron:
        return render(request, f"{KEY}/partials/job_modal.html", dict(
            job={"id": None, "label": label,
                 "cron": cron, "enabled": enabled, "steps": steps,
                 "notify_start": notify_start, "notify_end": notify_end},
            actions=get_registered_actions(),
            error="Name und Cron-Ausdruck sind Pflichtfelder.",
            container_id=_C_ID, loading_id=_L_ID,
        ), status_code=422)

    job_id = uuid.uuid4().hex[:12]
    create_job(job_id, label, cron, enabled, steps,
               notify_start=notify_start, notify_end=notify_end)
    return render(request, f"{KEY}/partials/tab.html", _list_ctx())


@router.post(f"/ui/{KEY}/job/{{job_id}}/update", response_class=HTMLResponse)
async def scheduler_job_save(job_id: str, request: Request):
    from astrapi.core.modules.scheduler.engine import update_job, get_registered_actions
    form = await request.form()

    label        = form.get("label", "").strip()
    cron         = form.get("cron", "").strip()
    enabled      = "1" in form.getlist("enabled")
    steps        = list(form.getlist("steps"))
    notify_start = "1" in form.getlist("notify_start")
    notify_end   = "1" in form.getlist("notify_end")

    if not label or not cron:
        from astrapi.core.modules.scheduler.engine import get_job
        job = get_job(job_id) or {"id": job_id}
        job.update({"label": label, "cron": cron, "enabled": enabled, "steps": steps,
                    "notify_start": notify_start, "notify_end": notify_end})
        return render(request, f"{KEY}/partials/job_modal.html", dict(
            job=job,
            actions=get_registered_actions(),
            error="Label und Cron-Ausdruck sind Pflichtfelder.",
            container_id=_C_ID, loading_id=_L_ID,
        ), status_code=422)

    update_job(job_id, label, cron, enabled, steps,
               notify_start=notify_start, notify_end=notify_end)
    return render(request, f"{KEY}/partials/tab.html", _list_ctx())


# ── Trigger ────────────────────────────────────────────────────────────────────

@router.post(f"/ui/{KEY}/job/{{job_id}}/trigger", response_class=HTMLResponse)
def scheduler_job_trigger(job_id: str, request: Request):
    from astrapi.core.modules.scheduler.engine import trigger_job
    trigger_job(job_id)
    return render(request, f"{KEY}/partials/list.html", _list_ctx())
