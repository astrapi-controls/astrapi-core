"""app/modules/hosts/jobs.py – Scheduler-Job für das Hosts-Modul.

Prüft ob alle aktivierten Hosts per TCP erreichbar sind und
schreibt das Ergebnis als 'reachable' in den Host-Eintrag.
"""
import logging
import socket

log = logging.getLogger(__name__)


def _notify(title: str, message: str, event: str) -> None:
    """Sendet eine Benachrichtigung mit source='hosts'."""
    try:
        from core.modules.notify import engine as notify
        notify.send(title=title, message=message, event=event, source="hosts", tags=["host"])
    except Exception as e:
        log.debug("hosts.check: Notify nicht verfügbar: %s", e)


def check_hosts() -> None:
    """Versucht alle aktivierten Hosts per TCP zu erreichen.

    Nutzt den konfigurierten Port (Standard: 22).
    Schreibt 'reachable: true/false' in den jeweiligen Storage-Eintrag.
    """
    from .storage import store

    hosts = store.list()
    enabled = {hid: h for hid, h in hosts.items() if h.get("enabled", True)}

    if not enabled:
        log.info("hosts.check: Keine aktivierten Hosts")
        return

    try:
        from core.ui.settings_registry import get as _srget
        connect_timeout = int(_srget("module.hosts.connect_timeout") or 10)
    except Exception:
        connect_timeout = 10

    for host_id, host in enabled.items():
        ip            = host.get("ip", "").strip()
        port          = int(host.get("port", 22))
        prev_reachable = host.get("reachable")  # None beim ersten Lauf
        label         = host.get("label") or host.get("name") or host_id

        if not ip:
            log.warning("hosts.check: Host '%s' hat keine IP", host_id)
            continue

        try:
            with socket.create_connection((ip, port), timeout=connect_timeout):
                reachable = True
        except OSError:
            reachable = False

        try:
            store.update(host_id, {"reachable": reachable})
        except KeyError:
            pass

        log.info("hosts.check: %s (%s:%d) → %s", host_id, ip, port,
                 "erreichbar" if reachable else "nicht erreichbar")

        # Host nicht mehr erreichbar (Zustandsänderung oder erster Lauf)
        if not reachable and prev_reachable is not False:
            _notify(
                title   = f"Host nicht erreichbar: {label}",
                message = f"{ip}:{port} antwortet nicht.",
                event   = "warning",
            )
        # Host wieder erreichbar (war zuvor down)
        elif reachable and prev_reachable is False:
            _notify(
                title   = f"Host wieder erreichbar: {label}",
                message = f"{ip}:{port} antwortet wieder.",
                event   = "success",
            )
