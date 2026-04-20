"""core/modules/system/api.py – FastAPI-Router für /api/system/"""
from fastapi import APIRouter
from .engine import collect, collect_cached
from . import updater as _updater

router = APIRouter()


# ── Systeminfo ────────────────────────────────────────────────────────────────

@router.get("/")
def get_sysinfo():
    return collect()


@router.get("/cpu")
def get_cpu():
    return collect_cached().get("cpu", {})


@router.get("/ram")
def get_ram():
    return collect_cached().get("mem", {})


@router.get("/disk")
def get_disk():
    return collect_cached().get("disks", [])


# ── Updater ───────────────────────────────────────────────────────────────────

@router.get("/update-status")
def get_update_status():
    status = _updater.get_status()
    if not status["packages"]:
        status["packages"] = _updater.get_packages_with_versions()
    return status


@router.post("/check")
def check_updates():
    return {"packages": _updater.check_updates()}


@router.post("/update")
def run_update():
    return {"started": _updater.run_update()}
