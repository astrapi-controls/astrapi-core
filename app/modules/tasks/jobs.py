"""app/modules/tasks/jobs.py – Scheduler-Job für das Tasks-Modul.

Führt alle aktivierten Tasks sequenziell aus.
"""
import logging
import subprocess

log = logging.getLogger(__name__)


def _notify(title: str, message: str, event: str) -> None:
    """Sendet eine Benachrichtigung mit source='tasks'."""
    try:
        from core.modules.notify import engine as notify
        notify.send(title=title, message=message, event=event, source="tasks", tags=["task"])
    except Exception as e:
        log.debug("tasks.run: Notify nicht verfügbar: %s", e)


def run_tasks() -> None:
    """Führt alle aktivierten Tasks aus.

    Der 'command' jedes Tasks wird als Shell-Kommando ausgeführt.
    Fehler werden geloggt aber nicht als Ausnahme weitergegeben,
    damit nachfolgende Tasks trotzdem laufen.
    """
    from .storage import store

    tasks = store.list()
    enabled = {tid: t for tid, t in tasks.items() if t.get("enabled", True)}

    if not enabled:
        log.info("tasks.run: Keine aktivierten Tasks")
        return

    for task_id, task in enabled.items():
        command = task.get("command", "").strip()
        label   = task.get("label") or task.get("name") or task_id

        if not command:
            log.info("tasks.run: Task '%s' hat kein Kommando, übersprungen", task_id)
            continue

        try:
            from core.ui.settings_registry import get as _srget
            timeout = int(_srget("module.tasks.timeout") or 300)
        except Exception:
            timeout = 300

        log.info("tasks.run: Task '%s' → %s", task_id, command)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                log.info("tasks.run: Task '%s' erfolgreich", task_id)
                _notify(
                    title   = f"Task erfolgreich: {label}",
                    message = "Erfolgreich abgeschlossen.",
                    event   = "success",
                )
            else:
                msg = f"Exit-Code {result.returncode}: {result.stderr[:300]}"
                log.warning("tasks.run: Task '%s' %s", task_id, msg)
                _notify(
                    title   = f"Task fehlgeschlagen: {label}",
                    message = msg,
                    event   = "error",
                )
        except subprocess.TimeoutExpired:
            log.error("tasks.run: Task '%s' Timeout nach %ds", task_id, timeout)
            _notify(
                title   = f"Task Timeout: {label}",
                message = f"Abgebrochen nach {timeout} Sekunden.",
                event   = "error",
            )
        except Exception as e:
            log.error("tasks.run: Task '%s' Fehler: %s", task_id, e)
            _notify(
                title   = f"Task Fehler: {label}",
                message = str(e),
                event   = "error",
            )
