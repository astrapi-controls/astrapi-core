"""dev_app/modules/demo_items/ui.py – FastAPI-Router"""

from pathlib import Path

from astrapi_core.ui.crud_blueprint import make_crud_router
from .storage import store, KEY

_DIR   = Path(__file__).parent
router = make_crud_router(
    store, KEY,
    schema_path=str(_DIR / "schema.yaml"),
    label="Demo Item",
    description_field="description",
)
