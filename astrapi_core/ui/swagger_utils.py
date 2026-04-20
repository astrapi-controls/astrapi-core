# core/ui/swagger_utils.py
#
# Generiert eine OpenAPI-Spec aus den registrierten Flask-Routen.
#
# Tags:    automatisch aus URL-Segment  → /ui/hosts/* → "hosts"
# Summary: automatisch aus URL-Muster   → /ui/hosts/<id>/edit → "Edit Host Modal"
# Methoden: exakt aus Flask-Rule, keine Extrapolation
#
# Manueller Override per Decorator:
#   from astrapi_core.ui.swagger_utils import ui_meta
#   @ui_meta(tag="hosts", summary="Load Hosts Tab", description="...")
#   def hosts_tab(): ...

from pathlib import Path
import re


# ── Decorator ─────────────────────────────────────────────────────────────────

def ui_meta(tag: str = None, summary: str = None, description: str = None):
    """Setzt Tag, Summary und/oder Description für eine Flask-View manuell."""
    def decorator(func):
        if tag:        setattr(func, "_ui_tag",         tag)
        if summary:    setattr(func, "_ui_summary",     summary)
        if description:setattr(func, "_ui_description", description)
        return func
    return decorator


# Rückwärtskompatibel
def ui_tag(tag_name: str):
    """Decorator: setzt nur den Tag (Kurzform von ui_meta)."""
    def decorator(func):
        setattr(func, "_ui_tag", tag_name)
        return func
    return decorator


# ── Tag aus URL ───────────────────────────────────────────────────────────────

def _tag_from_url(rule: str) -> str:
    """/ui/<key>/... → key  |  /<key> → key  |  / → navigation"""
    m = re.match(r"^/ui/([^/<]+)", rule)
    if m:
        return m.group(1)
    m = re.match(r"^/([^/<]+)$", rule)
    if m:
        return m.group(1)
    return "navigation"


# ── Summary aus URL ───────────────────────────────────────────────────────────

# Bekannte URL-Segmente → lesbarer Begriff
_SEGMENT_LABELS = {
    "content": "Content",
    "list":   "List",
    "create": "Create",
    "edit":   "Edit",
    "delete": "Delete",
    "toggle": "Toggle",
    "save":   "Save",
    "docs":   "Swagger UI",
}

def _to_singular(word: str) -> str:
    """Plural-URL-Segment → lesbarer Singular-Name: 'hosts' → 'Host'."""
    return (word[:-1] if word.endswith("s") else word).title()


def _summary_from_url(rule: str, method: str) -> str:
    """Leitet einen sprechenden Summary-Text aus URL-Muster + HTTP-Methode ab.

    Beispiele:
      GET  /ui/hosts/tab              → "Load Hosts Tab"
      GET  /ui/hosts/<host_id>/edit   → "Edit Host Modal"
      GET  /ui/hosts/<host_id>/delete → "Delete Host Confirmation"
      GET  /ui/hosts/create           → "Create Host Modal"
      POST /ui/settings/save/global   → "Save Global Settings"
      GET  /hosts                     → "Hosts Page"
      GET  /                          → "Root Redirect"
    """
    # Root
    if rule == "/":
        return "Root Redirect"

    parts = [p for p in rule.split("/") if p]

    # /<key>  → "<Key> Page"
    if len(parts) == 1 and not parts[0].startswith("<"):
        label = _to_singular(parts[0])
        return f"{label} Page"

    # /ui/<resource>/...
    if parts and parts[0] == "ui" and len(parts) >= 2:
        resource = parts[1]
        resource_label = _to_singular(resource)
        remaining = parts[2:]

        # /ui/<resource>/create
        if len(remaining) == 1 and remaining[0] == "create":
            return f"Create {resource_label} Modal"

        # /ui/<resource>/tab|list
        if len(remaining) == 1 and remaining[0] in _SEGMENT_LABELS:
            action = _SEGMENT_LABELS[remaining[0]]
            return f"Load {resource_label} {action}"

        # /ui/<resource>/<id>/edit|delete|toggle
        if len(remaining) == 2 and remaining[0].startswith("<"):
            action = _SEGMENT_LABELS.get(remaining[1], remaining[1].title())
            suffix = {
                "edit":   "Modal",
                "delete": "Confirmation",
                "toggle": "Confirmation",
                "create": "Modal",
            }.get(remaining[1], "")
            return f"{action} {resource_label} {suffix}".strip()

        # /ui/<resource>/save/<scope>  → "Save <scope> Settings"
        if len(remaining) >= 2 and remaining[0] == "save":
            scope = remaining[1]
            if scope.startswith("<"):
                scope = "Module"
            return f"Save {scope.title()} Settings"

    # Fallback: Segmente zusammensetzen
    readable = " ".join(
        _SEGMENT_LABELS.get(p, p.title())
        for p in parts
        if not p.startswith("<") and p != "ui"
    )
    return readable or rule


# ── Spec aufbauen ─────────────────────────────────────────────────────────────

def add_ui_routes_to_spec(app, project_root: Path) -> None:
    """Routen-Dokumentation – bei FastAPI nicht mehr nötig (OpenAPI ist eingebaut)."""
    pass


# ── Endpunkte registrieren ────────────────────────────────────────────────────

def register_ui_docs(app, project_root: Path, swagger_html_path: Path) -> None:
    """Registriert /ui/docs und /ui/openapi.json an der FastAPI-App."""
    from fastapi.responses import HTMLResponse, JSONResponse

    # App-Name aus FastAPI-Titel ableiten (ohne " API"-Suffix)
    app_name = getattr(app, "title", "Astrapi").removesuffix(" API")

    try:
        from apispec import APISpec
        _spec = APISpec(
            title=f"{app_name} UI-Routen",
            version="1.0.0",
            openapi_version="3.0.2",
            info={"description": "UI-Routen: HTMX-Partials, Modals, Seiten"},
        )
    except ImportError:
        return  # apispec nicht installiert – UI-Docs überspringen

    @app.get("/ui/docs", response_class=HTMLResponse, include_in_schema=False)
    def ui_docs():
        if not swagger_html_path.exists():
            return HTMLResponse("<p>swagger.html nicht gefunden</p>", status_code=404)
        html = swagger_html_path.read_text(encoding="utf-8")
        html = html.replace("{{OPENAPI_URL}}", "/ui/openapi.json")
        html = html.replace("{{TITLE}}", f"{app_name} – UI Docs")
        return HTMLResponse(html)

    @app.get("/ui/openapi.json", response_class=JSONResponse, include_in_schema=False)
    def ui_openapi_json():
        return JSONResponse(_spec.to_dict())
