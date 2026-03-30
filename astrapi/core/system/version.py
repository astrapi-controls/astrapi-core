"""core/system/version.py – Liest App- und Core-Metadaten aus app.yaml / core.yaml."""
from pathlib import Path


def _read_yaml(yaml_path: Path) -> dict:
    try:
        import yaml
        with open(yaml_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_app_version(app_root: Path, default: str = "—") -> str:
    return str(_read_yaml(app_root / "app.yaml").get("version", default))


def get_app_name(app_root: Path, default: str = "app") -> str:
    return str(_read_yaml(app_root / "app.yaml").get("name", default))


def get_display_name(app_root: Path, default: str = "App") -> str:
    return str(_read_yaml(app_root / "app.yaml").get("display_name", default))


def _clean_version(v: str) -> str:
    """Entfernt den lokalen Hash-Teil (z.B. '+gabc123.d20260330'), behält .devN."""
    return v.split("+")[0]


def get_core_version(core_root: Path, default: str = "—") -> str:
    try:
        from importlib.metadata import version
        return _clean_version(version("astrapi-core"))
    except Exception:
        return str(_read_yaml(core_root / "core.yaml").get("version", default))
