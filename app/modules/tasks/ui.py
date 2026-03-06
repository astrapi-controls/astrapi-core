"""app/modules/tasks/ui.py – Flask-Blueprint für Tasks UI-Routen."""

from flask import Blueprint, render_template, request
from .storage import store

bp = Blueprint("tasks_ui", __name__)


@bp.route("/ui/tasks/tab")
def tasks_tab():
    return render_template(
        "tasks/partials/list.html",
        tasks=store.list(),
        container_id="tab-tasks",
        loading_id="tasks-loading",
    )


@bp.route("/ui/tasks/list")
def tasks_list():
    return render_template(
        "tasks/partials/list.html",
        tasks=store.list(),
        container_id="tab-tasks",
        loading_id="tasks-loading",
    )


@bp.route("/ui/tasks/create")
def tasks_create_modal():
    container_id = request.args.get("container_id", "tab-tasks")
    loading_id   = request.args.get("loading_id", "tasks-loading")
    return render_template(
        "tasks/partials/create_modal.html",
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/tasks/<task_id>/edit")
def tasks_edit_modal(task_id: str):
    container_id = request.args.get("container_id", "tab-tasks")
    loading_id   = request.args.get("loading_id", "tasks-loading")
    task = store.get(task_id)
    if task is None:
        return "Task nicht gefunden", 404
    return render_template(
        "tasks/partials/edit_modal.html",
        task_id=task_id,
        task=task,
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/tasks/<task_id>/delete")
def tasks_delete_modal(task_id: str):
    container_id = request.args.get("container_id", "tab-tasks")
    loading_id   = request.args.get("loading_id", "tasks-loading")
    task         = store.get(task_id) or {}
    return render_template(
        "partials/confirm_modal.html",
        description=task.get("description", task_id),
        verb="löschen",
        confirm_url=f"/api/tasks/{task_id}/delete",
        method="delete",
        container_id=container_id,
        loading_id=loading_id,
    )


@bp.route("/ui/tasks/<task_id>/toggle")
def tasks_toggle_modal(task_id: str):
    container_id = request.args.get("container_id", "tab-tasks")
    loading_id   = request.args.get("loading_id", "tasks-loading")
    task         = store.get(task_id) or {}
    enabled      = request.args.get("enabled", "True")
    verb         = "deaktivieren" if enabled == "True" else "aktivieren"
    return render_template(
        "partials/confirm_modal.html",
        description=task.get("description", task_id),
        verb=verb,
        confirm_url=f"/api/tasks/{task_id}/toggle",
        method="post",
        container_id=container_id,
        loading_id=loading_id,
    )
