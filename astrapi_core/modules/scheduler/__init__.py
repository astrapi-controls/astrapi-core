"""core/modules/scheduler – Cron-Scheduler-Modul für AstrapiFlaskUi.

Projekte konfigurieren den Scheduler vor dem App-Start:

    from astrapi_core.modules.scheduler.engine import configure, init

    configure(job_fn=my_job, get_setting=..., set_setting=..., job_name="Sync")
    init()
"""
from astrapi_core.ui import Module
from .api import router
from .ui import router as ui_router

module = Module(
    key        = "scheduler",
    label      = "Scheduler",
    api_router = router,
    ui_router  = ui_router,
    nav_group  = "System",
)
