"""core/modules/settings/__init__.py – Framework-Einstellungen Modul."""

from astrapi_core.ui import Module
from .ui import router as ui_router

module = Module(
    key       = "settings",
    label     = "Einstellungen",
    nav_group = "System",
    ui_router = ui_router,
)
