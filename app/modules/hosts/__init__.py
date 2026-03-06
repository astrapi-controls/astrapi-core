"""app/modules/hosts/__init__.py – Hosts-Modul Selbst-Registrierung."""

from app.modules._base import AstrapiModule
from .api import router
from .ui import bp

module = AstrapiModule(
    key         = "hosts",
    label       = "Hosts",
    icon        = "server",
    api_router  = router,
    ui_blueprint= bp,
    nav_group   = "Module",
    nav_default = True,
    settings_template = "hosts/partials/settings_section.html",
    settings_defaults = {
        "default_port":    "22",
        "default_user":    "root",
        "connect_timeout": "10",
    },
)
