"""app/modules/hosts/jobs.py – Scheduler-Job für das Hosts-Modul.

Prüft ob alle aktivierten Hosts per TCP erreichbar sind und
schreibt das Ergebnis als 'reachable' in den Host-Eintrag.
"""
import logging
import socket

log = logging.getLogger(__name__)


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

    for host_id, host in enabled.items():
        ip   = host.get("ip", "").strip()
        port = int(host.get("port", 22))

        if not ip:
            log.warning("hosts.check: Host '%s' hat keine IP", host_id)
            continue

        try:
            with socket.create_connection((ip, port), timeout=5):
                reachable = True
        except OSError:
            reachable = False

        try:
            store.update(host_id, {"reachable": reachable})
        except KeyError:
            pass

        log.info("hosts.check: %s (%s:%d) → %s", host_id, ip, port,
                 "erreichbar" if reachable else "nicht erreichbar")
