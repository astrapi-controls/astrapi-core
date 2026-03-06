"""app/modules/hosts/api.py – FastAPI-Router für /api/hosts/"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .storage import store

router = APIRouter()


class HostIn(BaseModel):
    description: Optional[str] = ""
    ip:          Optional[str] = ""
    port:        Optional[int] = 22
    tags:        Optional[str] = ""
    enabled:     bool          = True


@router.get("/")
def list_hosts():
    hosts = store.list()
    return {"hosts": hosts, "total": len(hosts)}

@router.get("/{host_id}")
def get_host(host_id: str):
    host = store.get(host_id)
    if host is None:
        raise HTTPException(404, f"Host '{host_id}' nicht gefunden")
    return host

@router.post("/create")
def create_host(host_id: str, host: HostIn):
    try:
        return {"created": host_id, "host": store.create(host_id, host.model_dump())}
    except KeyError as e:
        raise HTTPException(409, str(e))

@router.put("/{host_id}/edit")
def edit_host(host_id: str, host: HostIn):
    try:
        return {"updated": host_id, "host": store.update(host_id, host.model_dump())}
    except KeyError as e:
        raise HTTPException(404, str(e))

@router.post("/{host_id}/toggle")
def toggle_host(host_id: str):
    try:
        enabled = store.toggle(host_id)
        return {"host_id": host_id, "enabled": enabled}
    except KeyError as e:
        raise HTTPException(404, str(e))

@router.delete("/{host_id}/delete")
def delete_host(host_id: str):
    try:
        store.delete(host_id)
        return {"deleted": host_id}
    except KeyError as e:
        raise HTTPException(404, str(e))
