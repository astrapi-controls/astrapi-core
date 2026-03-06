"""app/modules/hosts/ui.py – Flask-Blueprint für Hosts UI-Routen (Modals, Tab)."""

from flask import Blueprint, render_template, request
from .storage import store

bp = Blueprint("hosts_ui", __name__)


@bp.route("/ui/hosts/tab")
def hosts_tab():
    return render_template(
        "hosts/partials/list.html",
        hosts=store.list(),
        container_id="tab-hosts",
        loading_id="hosts-loading",
    )


@bp.route("/ui/hosts/list")
def hosts_list():
    return render_template(
        "hosts/partials/list.html",
        hosts=store.list(),
        container_id="tab-hosts",
        loading_id="hosts-loading",
    )


@bp.route("/ui/hosts/create")
def hosts_create_modal():
    container_id = request.args.get("container_id", "tab-hosts")
    loading_id   = request.args.get("loading_id", "hosts-loading")
    return render_template(
        "hosts/partials/create_modal.html",
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/hosts/<host_id>/edit")
def hosts_edit_modal(host_id: str):
    container_id = request.args.get("container_id", "tab-hosts")
    loading_id   = request.args.get("loading_id", "hosts-loading")
    host = store.get(host_id)
    if host is None:
        return "Host nicht gefunden", 404
    return render_template(
        "hosts/partials/edit_modal.html",
        host_id=host_id,
        host=host,
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/hosts/<host_id>/delete")
def hosts_delete_modal(host_id: str):
    container_id = request.args.get("container_id", "tab-hosts")
    loading_id   = request.args.get("loading_id", "hosts-loading")
    host         = store.get(host_id) or {}
    return render_template(
        "partials/confirm_modal.html",
        description=host.get("description", host_id),
        verb="löschen",
        confirm_url=f"/api/hosts/{host_id}/delete",
        method="delete",
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/hosts/<host_id>/toggle")
def hosts_toggle_modal(host_id: str):
    container_id = request.args.get("container_id", "tab-hosts")
    loading_id   = request.args.get("loading_id", "hosts-loading")
    host         = store.get(host_id) or {}
    enabled      = request.args.get("enabled", "True")
    verb         = "deaktivieren" if enabled == "True" else "aktivieren"
    return render_template(
        "partials/confirm_modal.html",
        description=host.get("description", host_id),
        verb=verb,
        confirm_url=f"/api/hosts/{host_id}/toggle",
        method="post",
        container_id=container_id,
        loading_id=loading_id,
    )
