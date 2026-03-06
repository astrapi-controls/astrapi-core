"""
core/ui/page_factory.py  –  Automatische Page- und Tab-Routen

URL-Schema:
  GET /ui/<key>       → App-Shell (index.html), HTMX triggert /ui/<key>/tab
  GET /<key>          → Redirect → /ui/<key>   (Bookmark-Kompatibilität)
  GET /ui/<key>/tab   → Tab-Partial (HTMX-Ziel)
  GET /ui/<key>/list  → Listen-Partial (HTMX-Polling / Refresh)

Für Module mit eigenem Blueprint (shell_only_keys) werden nur
Shell + Redirect registriert — Tab/List kommen vom Blueprint selbst.

/api/... bleibt ausschließlich FastAPI (JSON-Endpunkte).
/ui/...  ist ausschließlich Flask  (HTML-Partials, Modals, Seiten).
"""

from flask import Flask, render_template, redirect


def _label(key: str, nav_items: list[dict]) -> str:
    return next(
        (it["label"] for it in nav_items if not it.get("separator") and it["key"] == key),
        key.replace("_", " ").title(),
    )


def make_shell(resource_key: str, nav_items: list[dict]) -> callable:
    """App-Shell-View unter /ui/<key>."""
    title       = _label(resource_key, nav_items)
    initial_url = f"/ui/{resource_key}/tab"

    def shell():
        return render_template(
            "index.html",
            active_tab=resource_key,
            initial_content_url=initial_url,
            title=title,
        )

    shell.__name__ = f"shell_{resource_key}"
    return shell


def make_redirect(resource_key: str) -> callable:
    """Redirect /<key> → /ui/<key> für Bookmark-Kompatibilität."""
    def redir():
        return redirect(f"/ui/{resource_key}")

    redir.__name__ = f"redir_{resource_key}"
    return redir


def make_tab(resource_key: str, nav_items: list[dict]) -> callable:
    """Tab-Partial unter /ui/<key>/tab."""
    title        = _label(resource_key, nav_items)
    list_partial = f"partials/lists/{resource_key}.html"

    def tab():
        return render_template(
            "partials/tab_wrapper.html",
            active_tab=resource_key,
            title=title,
            list_partial=list_partial,
            module=resource_key,
            container_id=f"tab-{resource_key}",
            loading_id=f"{resource_key}-loading",
        )

    tab.__name__ = f"tab_{resource_key}"
    return tab


def make_list(resource_key: str) -> callable:
    """Listen-Partial unter /ui/<key>/list."""
    list_partial = f"partials/lists/{resource_key}.html"

    def lst():
        return render_template(list_partial)

    lst.__name__ = f"list_{resource_key}"
    return lst


def register_pages(
    app: Flask,
    nav_items: list[dict],
    shell_only_keys: set[str] | None = None,
) -> None:
    """Registriert Routen für jeden Nav-Eintrag.

    shell_only_keys: Keys für die nur Shell + Redirect registriert werden
                     (Tab/List kommen vom Modul-Blueprint).
    """
    shell_only = shell_only_keys or set()

    for item in nav_items:
        if item.get("separator"):
            continue

        key = item["key"]

        # /ui/<key>  → App-Shell (immer)
        app.add_url_rule(f"/ui/{key}", endpoint=f"shell_{key}", view_func=make_shell(key, nav_items))
        # /<key>     → Redirect → /ui/<key> (immer)
        app.add_url_rule(f"/{key}",   endpoint=f"redir_{key}", view_func=make_redirect(key))

        if key not in shell_only:
            # /ui/<key>/tab   → Tab-Partial
            app.add_url_rule(f"/ui/{key}/tab",  endpoint=f"tab_{key}",  view_func=make_tab(key, nav_items))
            # /ui/<key>/list  → Listen-Partial
            app.add_url_rule(f"/ui/{key}/list", endpoint=f"list_{key}", view_func=make_list(key))
