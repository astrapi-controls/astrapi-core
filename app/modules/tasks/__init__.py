from pathlib import Path
from core.ui.module_loader import load_modul
from .api import router
from .ui import bp

module = load_modul(Path(__file__).parent, Path(__file__).parent.name, router, bp)

# Scheduler-Aktion registrieren
try:
    from core.modules.scheduler.engine import register_action
    from .jobs import run_tasks
    register_action("tasks.run", "Tasks ausführen", run_tasks)
except Exception:
    pass
