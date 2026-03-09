"""app/modules/tasks/jobs.py – Scheduler-Job für das Tasks-Modul.

Führt alle aktivierten Tasks sequenziell aus.
"""
import logging
import subprocess

log = logging.getLogger(__name__)


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
        if not command:
            log.info("tasks.run: Task '%s' hat kein Kommando, übersprungen", task_id)
            continue

        log.info("tasks.run: Task '%s' → %s", task_id, command)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                log.info("tasks.run: Task '%s' erfolgreich", task_id)
            else:
                log.warning("tasks.run: Task '%s' Exit-Code %d: %s",
                            task_id, result.returncode, result.stderr[:200])
        except subprocess.TimeoutExpired:
            log.error("tasks.run: Task '%s' Timeout nach 300s", task_id)
        except Exception as e:
            log.error("tasks.run: Task '%s' Fehler: %s", task_id, e)
