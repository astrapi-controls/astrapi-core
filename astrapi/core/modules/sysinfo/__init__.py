"""core/modules/sysinfo/__init__.py – System-Informationen Modul."""

from astrapi.core.ui import Module
from .api import router
from .ui import router as ui_router

module = Module(
    key        = "sysinfo",
    label      = "System",
    icon       = "monitor",
    api_router = router,
    ui_router  = ui_router,
    nav_group  = "System",
)
