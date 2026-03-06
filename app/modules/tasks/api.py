"""app/modules/tasks/api.py – FastAPI-Router für /api/tasks/"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .storage import store

router = APIRouter()


class TaskIn(BaseModel):
    description: Optional[str] = ""
    command:     Optional[str] = ""
    schedule:    Optional[str] = "0 * * * *"
    enabled:     bool          = True


@router.get("/")
def list_tasks():
    tasks = store.list()
    return {"tasks": tasks, "total": len(tasks)}

@router.get("/{task_id}")
def get_task(task_id: str):
    task = store.get(task_id)
    if task is None:
        raise HTTPException(404, f"Task '{task_id}' nicht gefunden")
    return task

@router.post("/create")
def create_task(task_id: str, task: TaskIn):
    try:
        return {"created": task_id, "task": store.create(task_id, task.model_dump())}
    except KeyError as e:
        raise HTTPException(409, str(e))

@router.put("/{task_id}/edit")
def edit_task(task_id: str, task: TaskIn):
    try:
        return {"updated": task_id, "task": store.update(task_id, task.model_dump())}
    except KeyError as e:
        raise HTTPException(404, str(e))

@router.post("/{task_id}/toggle")
def toggle_task(task_id: str):
    try:
        enabled = store.toggle(task_id)
        return {"task_id": task_id, "enabled": enabled}
    except KeyError as e:
        raise HTTPException(404, str(e))

@router.delete("/{task_id}/delete")
def delete_task(task_id: str):
    try:
        store.delete(task_id)
        return {"deleted": task_id}
    except KeyError as e:
        raise HTTPException(404, str(e))
