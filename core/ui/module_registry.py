"""
core/ui/module_registry.py  –  AstrapiFlaskUi V3  Modul-Registry

Scannt app/modules/ nach AstrapiModule-Instanzen und registriert:
  - FastAPI-Router        unter /api/<key>/
  - Flask-Blueprint       (UI-Routen, Modals)
  - Template-Loader       (modul-eigene templates/ werden eingefügt)
  - Nav-Eintrag           (in nav_items-Liste)
  - Einstellungs-Sektion  (für /settings)

Aufruf in core/ui/app.py:
    from .module_registry import load_modules, register_flask_modules
    modules = load_modules(app_root)
    register_flask_modules(flask_app, modules)

Und in app/api/fastapi_app.py:
    from core.ui.module_registry import load_modules, register_fastapi_modules
    modules = load_modules(app_root)
    register_fastapi_modules(fastapi_app, modules)
"""

from __future__ import annotations

import importlib.util
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask
    from fastapi import FastAPI


def load_modules(app_root: Path) -> list:
    """Scannt app/modules/ und gibt alle AstrapiModule-Instanzen zurück.

    Ein Modul wird erkannt wenn app/modules/<name>/__init__.py eine
    Variable `module` vom Typ AstrapiModule exportiert.
    """
    from app.modules._base import AstrapiModule

    modules_dir = app_root / "modules"
    if not modules_dir.exists():
        return []

    found: list[AstrapiModule] = []

    for entry in sorted(modules_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue

        init_file = entry / "__init__.py"
        if not init_file.exists():
            continue

        try:
            spec = importlib.util.spec_from_file_location(
                f"app.modules.{entry.name}", init_file
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            instance = getattr(mod, "module", None)
            if instance is None or not isinstance(instance, AstrapiModule):
                warnings.warn(
                    f"Modul '{entry.name}': keine AstrapiModule-Instanz 'module' gefunden"
                )
                continue

            # Modul-Root setzen damit Templates etc. gefunden werden
            instance.module_root = entry
            found.append(instance)

        except Exception as e:
            warnings.warn(f"Modul '{entry.name}' konnte nicht geladen werden: {e}")

    return found


def register_flask_modules(flask_app, modules: list, jinja_loaders: list) -> None:
    """Registriert Flask-Blueprints und Template-Loader aller Module."""
    from jinja2 import FileSystemLoader

    for mod in modules:
        # ── Template-Loader des Moduls ────────────────────────────────────────
        if mod.module_root:
            tpl_dir = mod.module_root / "templates"
            if tpl_dir.exists():
                # Vor den App-Loaders einfügen (höchste Priorität)
                jinja_loaders.insert(0, FileSystemLoader(str(tpl_dir)))

        # ── Flask-Blueprint registrieren ──────────────────────────────────────
        if mod.ui_blueprint is not None:
            try:
                flask_app.register_blueprint(mod.ui_blueprint)
            except Exception as e:
                warnings.warn(f"Blueprint von Modul '{mod.key}' konnte nicht registriert werden: {e}")


def register_fastapi_modules(fastapi_app, modules: list) -> None:
    """Registriert FastAPI-Router aller Module."""
    for mod in modules:
        if mod.api_router is not None:
            try:
                fastapi_app.include_router(
                    mod.api_router,
                    prefix=f"/api/{mod.key}",
                    tags=[mod.key],
                )
            except Exception as e:
                warnings.warn(f"Router von Modul '{mod.key}' konnte nicht registriert werden: {e}")


def build_nav_items(modules: list, extra_yaml_path: Path | None = None) -> list[dict]:
    """Baut die komplette nav_items-Liste aus Modulen + optionaler YAML.

    Reihenfolge:
      1. Feste Einträge aus items.yaml (falls vorhanden) – ohne Modul-Keys
      2. Modul-Nav-Einträge (nach Modul-Reihenfolge in modules/)
      3. Einstellungen immer am Ende
    """
    items: list[dict] = []

    # ── Optionale statische Einträge aus items.yaml ───────────────────────────
    if extra_yaml_path and extra_yaml_path.exists():
        from .navigation import load_nav
        static_items = load_nav(extra_yaml_path)
        # Modul-Keys und settings aus YAML herausfiltern
        # (werden von Modulen selbst registriert)
        module_keys = {m.key for m in modules} | {"settings"}
        for item in static_items:
            if item.get("separator") or item.get("key") not in module_keys:
                items.append(item)

    # ── Modul-Nav-Einträge ────────────────────────────────────────────────────
    if modules:
        # Gruppe nur wenn tatsächlich Module vorhanden
        first_group = next((m.nav_group for m in modules if m.nav_group), None)
        if first_group or not items:
            # Separator vor den Modulen
            group_label = first_group or "Module"
            items.append({"separator": True, "group": group_label})

        for mod in modules:
            items.append(mod.to_nav_item())

    # ── Einstellungen immer zuletzt ───────────────────────────────────────────
    items.append({"separator": True, "group": "System"})
    items.append({
        "key":       "settings",
        "label":     "Einstellungen",
        "url":       "/ui/settings/tab",
        "icon":      "settings",
        "default":   False,
        "separator": False,
    })

    # ── Default setzen wenn noch keiner vorhanden ─────────────────────────────
    has_default = any(
        not i.get("separator") and i.get("default") for i in items
    )
    if not has_default:
        for item in items:
            if not item.get("separator"):
                item["default"] = True
                break

    return items
