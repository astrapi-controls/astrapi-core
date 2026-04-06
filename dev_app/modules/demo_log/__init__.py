from pathlib import Path
from astrapi.core.ui.module_loader import load_modul
from .ui import router as ui_router

module = load_modul(Path(__file__).parent, Path(__file__).parent.name, None, ui_router)
