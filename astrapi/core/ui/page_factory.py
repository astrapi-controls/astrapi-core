"""
core/ui/page_factory.py  –  Automatische Page- und Content-Routen (FastAPI)

URL-Schema:
  GET /<key>              → App-Shell (index.html), lädt /ui/<key>/content per HTMX
  GET /ui/<key>/content   → Inhalt-Partial (Nav-Klick + Reload + Refresh)

/api/... bleibt ausschließlich FastAPI (JSON).
/ui/...  HTML-Partials, Modals (FastAPI).
/<key>   ist die sichtbare Browser-URL.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


def _label(key: str, nav_items: list[dict]) -> str:
    return next(
        (it["label"] for it in nav_items if not it.get("separator") and it["key"] == key),
        key.replace("_", " ").title(),
    )


def register_pages(
    api,
    nav_items: list[dict],
    shell_only_keys: set[str] | None = None,
) -> None:
    """Registriert Shell- und Content-Route für jeden Nav-Eintrag."""
    from astrapi.core.ui.render import render

    shell_only = shell_only_keys or set()

    for item in nav_items:
        if item.get("separator"):
            continue

        key   = item["key"]
        title = _label(key, nav_items)

        # Closure-safe Werte binden
        _key           = key
        _title         = title
        _content_url   = f"/ui/{key}/content"

        def _make_shell(k, t, cu):
            def shell(request: Request):
                return render(request, "index.html", dict(
                    active_tab=k,
                    initial_content_url=cu,
                    title=t,
                ))
            shell.__name__ = f"shell_{k}"
            return shell

        def _make_content(k):
            list_partial = f"partials/lists/{k}.html"

            def content(request: Request):
                return render(request, list_partial)
            content.__name__ = f"content_{k}"
            return content

        api.add_api_route(
            f"/{_key}",
            _make_shell(_key, _title, _content_url),
            methods=["GET"],
            response_class=HTMLResponse,
        )

        if _key not in shell_only:
            api.add_api_route(
                f"/ui/{_key}/content",
                _make_content(_key),
                methods=["GET"],
                response_class=HTMLResponse,
            )
