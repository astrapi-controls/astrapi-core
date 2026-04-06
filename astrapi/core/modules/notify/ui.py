"""core/modules/notify/ui.py – FastAPI-Router für Benachrichtigungs-Kanäle und -Jobs."""

import uuid

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from astrapi.core.ui.render import render
from .engine import (
    KEY,
    list_channels, get_channel, create_channel, update_channel,
    list_jobs, get_job, create_job, update_job,
    get_registered_backends, get_registered_sources,
    test_channel as _test_channel, test_job as _test_job,
)
from .schema import ALL_EVENTS

router = APIRouter()

_CONTAINER_ID = f"tab-{KEY}"
_LOADING_ID   = f"{KEY}-loading"

_BUILTIN_BACKENDS = [
    ("ntfy",  "ntfy",  "Push-Benachrichtigungen via ntfy.sh oder eigenem Server"),
    ("email", "E-Mail", "Benachrichtigungen per SMTP (Gmail, Outlook, eigener Server …)"),
]


# ── Kontext-Helfer ────────────────────────────────────────────────────────────

def _ctx(**extra) -> dict:
    module_sources, scheduler_sources = _split_sources()
    return dict(
        key=KEY,
        label="Benachrichtigungen",
        channels=list_channels(),
        jobs=list_jobs(),
        all_sources={**module_sources, **scheduler_sources},
        container_id=_CONTAINER_ID,
        loading_id=_LOADING_ID,
        **extra,
    )


def _parse_channel_form(form) -> dict:
    """Liest und normalisiert alle Kanalformularfelder."""
    enabled = "1" in form.getlist("enabled")
    return {
        "label":               form.get("label", "").strip(),
        "backend":             form.get("backend", "ntfy"),
        "enabled":             enabled,
        # ntfy
        "ntfy_url":            form.get("ntfy_url", "https://ntfy.sh").strip(),
        "ntfy_topic":          form.get("ntfy_topic", "").strip(),
        "ntfy_token":          form.get("ntfy_token", "").strip(),
        "ntfy_verify_ssl":     "ntfy_verify_ssl" in form,
        # E-Mail
        "mail_smtp_host":      form.get("mail_smtp_host", "").strip(),
        "mail_smtp_port":      int(form.get("mail_smtp_port") or 587),
        "mail_smtp_user":      form.get("mail_smtp_user", "").strip(),
        "mail_smtp_password":  form.get("mail_smtp_password", "").strip(),
        "mail_smtp_tls":       "mail_smtp_tls" in form,
        "mail_from":           form.get("mail_from", "").strip(),
        "mail_to":             form.get("mail_to", "").strip(),
        "mail_subject_prefix": form.get("mail_subject_prefix", "[Notify]").strip(),
    }


def _parse_job_form(form) -> dict:
    """Liest und normalisiert alle Job-Formularfelder."""
    enabled = "1" in form.getlist("enabled")
    return {
        "label":      form.get("label", "").strip(),
        "channel_id": form.get("channel_id", "").strip(),
        "enabled":    enabled,
        "events":     list(form.getlist("events")),
        "sources":    list(form.getlist("sources")),
    }


def _split_sources() -> tuple[dict, dict]:
    """Trennt registrierte Quellen in Modul-Quellen und Scheduler-Jobs."""
    all_sources = get_registered_sources()
    try:
        from astrapi.core.modules.scheduler.engine import list_jobs as _sched_list
        sched_ids = {j["id"] for j in _sched_list()}
    except Exception:
        sched_ids = set()
    module_sources    = {k: v for k, v in all_sources.items() if k not in sched_ids}
    scheduler_sources = {k: v for k, v in all_sources.items() if k in sched_ids}
    return module_sources, scheduler_sources


# ── Gemeinsame Listen-View ────────────────────────────────────────────────────

@router.get(f"/ui/{KEY}/content", response_class=HTMLResponse)
def content(request: Request):
    return render(request, f"{KEY}/partials/list.html", _ctx())


# ── Kanal-Modale ──────────────────────────────────────────────────────────────

@router.get(f"/ui/{KEY}/backend-select", response_class=HTMLResponse)
def backend_select_modal(request: Request):
    return render(request, f"{KEY}/partials/backend_select_modal.html", dict(
        builtin_backends=_BUILTIN_BACKENDS,
        custom_backends=get_registered_backends(),
    ))


@router.get(f"/ui/{KEY}/create/{{backend}}", response_class=HTMLResponse)
def create_modal(backend: str, request: Request):
    return render(request, f"{KEY}/partials/channel_modal.html", dict(
        channel=None,
        channel_id=None,
        selected_backend=backend,
        title="Neuer Benachrichtigungskanal",
        submit_url=f"/ui/{KEY}/",
    ))


@router.get(f"/ui/{KEY}/{{channel_id}}/edit", response_class=HTMLResponse)
def edit_modal(channel_id: str, request: Request):
    channel = get_channel(channel_id)
    if channel is None:
        return HTMLResponse("Kanal nicht gefunden", status_code=404)
    return render(request, f"{KEY}/partials/channel_modal.html", dict(
        channel=channel,
        channel_id=channel_id,
        selected_backend=channel.get("backend", "ntfy"),
        title=f"Kanal bearbeiten ({channel.get('backend', 'ntfy')})",
        submit_url=f"/ui/{KEY}/{channel_id}/update",
    ))


@router.get(f"/ui/{KEY}/{{channel_id}}/delete", response_class=HTMLResponse)
def delete_modal(channel_id: str, request: Request):
    channel = get_channel(channel_id) or {}
    return render(request, "partials/confirm_modal.html", dict(
        description=channel.get("label", channel_id),
        verb="löschen",
        confirm_url=f"/api/{KEY}/{channel_id}",
        method="delete",
        reload_url=f"/ui/{KEY}/content",
        container_id=_CONTAINER_ID,
        loading_id=_LOADING_ID,
    ))


@router.get(f"/ui/{KEY}/{{channel_id}}/toggle", response_class=HTMLResponse)
def toggle_modal(channel_id: str, request: Request):
    channel = get_channel(channel_id) or {}
    enabled = request.query_params.get("enabled", "True")
    verb    = "deaktivieren" if enabled == "True" else "aktivieren"
    return render(request, "partials/confirm_modal.html", dict(
        description=channel.get("label", channel_id),
        verb=verb,
        confirm_url=f"/api/{KEY}/{channel_id}/toggle",
        method="patch",
        reload_url=f"/ui/{KEY}/content",
        container_id=_CONTAINER_ID,
        loading_id=_LOADING_ID,
    ))


# ── Kanal CRUD-Aktionen ───────────────────────────────────────────────────────

@router.post(f"/ui/{KEY}/", response_class=HTMLResponse)
async def create_apply(request: Request):
    channel_id = f"ch-{uuid.uuid4().hex[:8]}"
    form = await request.form()
    data = _parse_channel_form(form)
    try:
        create_channel(channel_id, data)
    except KeyError:
        return HTMLResponse("ID bereits vergeben", status_code=409)
    return render(request, f"{KEY}/partials/list.html", _ctx())


@router.post(f"/ui/{KEY}/{{channel_id}}/update", response_class=HTMLResponse)
async def edit_apply(channel_id: str, request: Request):
    form = await request.form()
    data = _parse_channel_form(form)
    try:
        update_channel(channel_id, data)
    except KeyError:
        return HTMLResponse("Kanal nicht gefunden", status_code=404)
    return render(request, f"{KEY}/partials/list.html", _ctx())


# ── Kanal-Test ────────────────────────────────────────────────────────────────

@router.post(f"/ui/{KEY}/{{channel_id}}/test", response_class=HTMLResponse)
def test_channel_view(channel_id: str, request: Request):
    ok, msg = _test_channel(channel_id)
    return _test_badge(request, ok, msg)


# ── Job-Modale ────────────────────────────────────────────────────────────────

@router.get(f"/ui/{KEY}/jobs/create", response_class=HTMLResponse)
def create_job_modal(request: Request):
    module_sources, scheduler_sources = _split_sources()
    return render(request, f"{KEY}/partials/job_modal.html", dict(
        job=None,
        job_id=None,
        title="Neuer Notify-Job",
        submit_url=f"/ui/{KEY}/jobs/",
        all_events=ALL_EVENTS,
        all_sources=module_sources,
        scheduler_sources=scheduler_sources,
        all_channels=list_channels(),
    ))


@router.get(f"/ui/{KEY}/jobs/{{job_id}}/edit", response_class=HTMLResponse)
def edit_job_modal(job_id: str, request: Request):
    job = get_job(job_id)
    if job is None:
        return HTMLResponse("Job nicht gefunden", status_code=404)
    module_sources, scheduler_sources = _split_sources()
    return render(request, f"{KEY}/partials/job_modal.html", dict(
        job=job,
        job_id=job_id,
        title="Job bearbeiten",
        submit_url=f"/ui/{KEY}/jobs/{job_id}/update",
        all_events=ALL_EVENTS,
        all_sources=module_sources,
        scheduler_sources=scheduler_sources,
        all_channels=list_channels(),
    ))


@router.get(f"/ui/{KEY}/jobs/{{job_id}}/delete", response_class=HTMLResponse)
def delete_job_modal(job_id: str, request: Request):
    job = get_job(job_id) or {}
    return render(request, "partials/confirm_modal.html", dict(
        description=job.get("label", job_id),
        verb="löschen",
        confirm_url=f"/api/{KEY}/jobs/{job_id}",
        method="delete",
        reload_url=f"/ui/{KEY}/content",
        container_id=_CONTAINER_ID,
        loading_id=_LOADING_ID,
    ))


@router.get(f"/ui/{KEY}/jobs/{{job_id}}/toggle", response_class=HTMLResponse)
def toggle_job_modal(job_id: str, request: Request):
    job     = get_job(job_id) or {}
    enabled = request.query_params.get("enabled", "True")
    verb    = "deaktivieren" if enabled == "True" else "aktivieren"
    return render(request, "partials/confirm_modal.html", dict(
        description=job.get("label", job_id),
        verb=verb,
        confirm_url=f"/api/{KEY}/jobs/{job_id}/toggle",
        method="patch",
        reload_url=f"/ui/{KEY}/content",
        container_id=_CONTAINER_ID,
        loading_id=_LOADING_ID,
    ))


# ── Job CRUD-Aktionen ─────────────────────────────────────────────────────────

@router.post(f"/ui/{KEY}/jobs/", response_class=HTMLResponse)
async def create_job_apply(request: Request):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    form = await request.form()
    data = _parse_job_form(form)
    try:
        create_job(job_id, data)
    except KeyError:
        return HTMLResponse("ID bereits vergeben", status_code=409)
    return render(request, f"{KEY}/partials/list.html", _ctx())


@router.post(f"/ui/{KEY}/jobs/{{job_id}}/update", response_class=HTMLResponse)
async def edit_job_apply(job_id: str, request: Request):
    form = await request.form()
    data = _parse_job_form(form)
    try:
        update_job(job_id, data)
    except KeyError:
        return HTMLResponse("Job nicht gefunden", status_code=404)
    return render(request, f"{KEY}/partials/list.html", _ctx())


# ── Job-Test ──────────────────────────────────────────────────────────────────

@router.post(f"/ui/{KEY}/jobs/{{job_id}}/test", response_class=HTMLResponse)
def test_job_view(job_id: str, request: Request):
    ok, msg = _test_job(job_id)
    return _test_badge(request, ok, msg)


def _test_badge(request: Request, ok: bool, msg: str):
    return render(request, f"{KEY}/partials/test_badge.html", {"ok": ok, "msg": msg})
