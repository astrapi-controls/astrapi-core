"""core/modules/system/__init__.py – System-Informationen + Updater."""

from pathlib import Path
from astrapi_core.ui import Module
from .api import router
from .ui import router as ui_router

module = Module(
    key        = "system",
    label      = "System",
    api_router = router,
    ui_router  = ui_router,
    nav_group  = "System",
)
