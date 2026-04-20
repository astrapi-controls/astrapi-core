from pathlib import Path
from astrapi_core.ui.module_loader import load_modul
from .api import router
from .ui import router as ui_router

module = load_modul(Path(__file__).parent, Path(__file__).parent.name, router, ui_router)
