"""app/modules/tasks/__init__.py – Tasks-Modul Selbst-Registrierung."""

from app.modules._base import AstrapiModule
from .api import router
from .ui import bp

module = AstrapiModule(
    key          = "tasks",
    label        = "Tasks",
    icon         = "clock",
    api_router   = router,
    ui_blueprint = bp,
    nav_group    = "Module",
    settings_template = "tasks/partials/settings_section.html",
    settings_defaults = {
        "default_schedule": "0 2 * * *",
        "max_retries":      "3",
        "timeout":          "300",
    },
)
