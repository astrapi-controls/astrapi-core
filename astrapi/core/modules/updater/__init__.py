from pathlib import Path
from astrapi.core.ui.module_loader import load_modul
from .api import router
from .ui import router as ui_router

module = load_modul(Path(__file__).parent, "updater", router, ui_router)
