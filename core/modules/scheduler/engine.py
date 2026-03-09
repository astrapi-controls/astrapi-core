# core/modules/scheduler/engine.py
"""Multi-Job Scheduler mit Action Registry.

Module registrieren Aktionen einmalig beim Start:

    from core.modules.scheduler.engine import register_action
    register_action("hosts.check", "Hosts prüfen", check_hosts)

Jobs werden in YamlStorage("scheduler_jobs") gespeichert und können
über die UI erstellt, bearbeitet und gelöscht werden.
"""
import logging
import threading
import time
from datetime import datetime
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger(__name__)

TIMEZONE = "Europe/Berlin"

# ── Action Registry ────────────────────────────────────────────────────────────

_actions: dict[str, dict] = {}


def register_action(key: str, label: str, fn: Callable) -> None:
    """Registriert eine Scheduler-Aktion.

    Args:
        key:   Eindeutiger Schlüssel, z.B. "hosts.check"
        label: Anzeigename in der UI
        fn:    Callable ohne Argumente
    """
    _actions[key] = {"label": label, "fn": fn}


def get_registered_actions() -> dict[str, str]:
    """Gibt {key: label} aller registrierten Aktionen zurück."""
    return {k: v["label"] for k, v in _actions.items()}


# ── Storage (lazy) ─────────────────────────────────────────────────────────────

def _jobs_store():
    from core.ui.storage import YamlStorage
    return YamlStorage("scheduler_jobs")


def _status_store():
    from core.ui.storage import YamlStorage
    return YamlStorage("scheduler_status")


# ── Scheduler Singleton ────────────────────────────────────────────────────────

_sch: BackgroundScheduler | None = None
_lock = threading.Lock()


def _get_sch() -> BackgroundScheduler:
    global _sch
    if _sch is None:
        _sch = BackgroundScheduler(timezone=TIMEZONE)
    return _sch


def init() -> None:
    """Startet den APScheduler und registriert alle konfigurierten Jobs."""
    sch = _get_sch()
    if sch.running:
        return
    _sync_jobs()
    sch.start()


def _sync_jobs() -> None:
    """Synchronisiert APScheduler-Jobs mit der Job-Storage."""
    sch = _get_sch()
    for apjob in sch.get_jobs():
        sch.remove_job(apjob.id)

    try:
        jobs = _jobs_store().list()
    except Exception as e:
        log.warning("scheduler_jobs Storage nicht verfügbar: %s", e)
        return

    for job_id, cfg in jobs.items():
        if not cfg.get("enabled", False):
            continue
        cron = cfg.get("cron", "").strip()
        if not cron:
            continue
        try:
            sch.add_job(
                func=_run_job,
                trigger=CronTrigger.from_crontab(cron, timezone=TIMEZONE),
                id=job_id,
                name=cfg.get("label", job_id),
                kwargs={"job_id": job_id},
                replace_existing=True,
                misfire_grace_time=300,
            )
        except Exception as e:
            log.error("Fehler beim Registrieren von Job '%s': %s", job_id, e)


# ── Job Execution ──────────────────────────────────────────────────────────────

def _run_job(job_id: str) -> None:
    """Führt alle Steps eines Jobs sequenziell aus."""
    cfg = _jobs_store().get(job_id)
    if not cfg:
        log.warning("Job '%s' nicht gefunden", job_id)
        return

    steps = cfg.get("steps", [])
    start = time.time()
    errors: list[str] = []

    for step_key in steps:
        action = _actions.get(step_key)
        if action is None:
            errors.append(f"Unbekannte Aktion: {step_key}")
            log.warning("Unbekannte Aktion '%s' in Job '%s'", step_key, job_id)
            continue
        try:
            log.info("Job '%s': Schritt '%s' startet", job_id, step_key)
            action["fn"]()
            log.info("Job '%s': Schritt '%s' abgeschlossen", job_id, step_key)
        except Exception as e:
            errors.append(f"{step_key}: {e}")
            log.error("Job '%s': Schritt '%s' fehlgeschlagen: %s", job_id, step_key, e)

    duration = f"{time.time() - start:.1f}s"
    status = "OK" if not errors else ("Fehler: " + "; ".join(errors))

    _status_store().upsert(job_id, {
        "last_run":      datetime.now().strftime("%d.%m.%Y %H:%M"),
        "last_status":   status,
        "last_duration": duration,
    })


def trigger_job(job_id: str) -> None:
    """Führt einen Job sofort in einem Hintergrundthread aus."""
    threading.Thread(target=_run_job, kwargs={"job_id": job_id}, daemon=True).start()


# ── Job CRUD ───────────────────────────────────────────────────────────────────

def _enrich(job_id: str, cfg: dict) -> dict:
    """Reichert Job-Config mit APScheduler-Status und letztem Laufstatus an."""
    sch = _get_sch()
    apjob = sch.get_job(job_id) if sch.running else None
    next_run = (
        apjob.next_run_time.strftime("%d.%m.%Y %H:%M")
        if apjob and apjob.next_run_time else None
    )
    try:
        status = _status_store().get(job_id) or {}
    except Exception:
        status = {}
    return {
        "id":            job_id,
        "label":         cfg.get("label", job_id),
        "cron":          cfg.get("cron", ""),
        "enabled":       cfg.get("enabled", False),
        "steps":         cfg.get("steps", []),
        "next_run":      next_run,
        "last_run":      status.get("last_run", ""),
        "last_status":   status.get("last_status", ""),
        "last_duration": status.get("last_duration", ""),
    }


def list_jobs() -> list[dict]:
    """Gibt alle Jobs mit Status zurück."""
    try:
        return [_enrich(jid, cfg) for jid, cfg in _jobs_store().list().items()]
    except Exception:
        return []


def get_job(job_id: str) -> dict | None:
    cfg = _jobs_store().get(job_id)
    return _enrich(job_id, cfg) if cfg else None


def create_job(job_id: str, label: str, cron: str, enabled: bool, steps: list[str]) -> dict:
    _jobs_store().create(job_id, {
        "label":   label,
        "cron":    cron,
        "enabled": enabled,
        "steps":   steps,
    })
    if _get_sch().running:
        _sync_jobs()
    return _enrich(job_id, _jobs_store().get(job_id))


def update_job(job_id: str, label: str, cron: str, enabled: bool, steps: list[str]) -> dict:
    _jobs_store().update(job_id, {
        "label":   label,
        "cron":    cron,
        "enabled": enabled,
        "steps":   steps,
    })
    if _get_sch().running:
        _sync_jobs()
    return _enrich(job_id, _jobs_store().get(job_id))


def delete_job(job_id: str) -> None:
    _jobs_store().delete(job_id)
    try:
        _status_store().delete(job_id)
    except KeyError:
        pass
    sch = _get_sch()
    if sch.running and sch.get_job(job_id):
        sch.remove_job(job_id)


def toggle_job(job_id: str) -> None:
    current = _jobs_store().get(job_id) or {}
    _jobs_store().update(job_id, {"enabled": not current.get("enabled", False)})
    if _get_sch().running:
        _sync_jobs()
