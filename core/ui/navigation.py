import yaml
from pathlib import Path


def load_nav(path: Path) -> list[dict]:
    """Lädt die Navigation aus einer YAML-Datei.

    Erwartet eine Liste von Einträgen mit:
      key:     eindeutiger URL-Schlüssel
      label:   Anzeigetext
      url:     HTMX-Tab-Endpunkt (z. B. /api/ui/<key>/tab)
      icon:    Icon-Name (siehe navigation/index.html Makro)
      default: true → dieser Eintrag wird beim Start geladen
    """
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []

    items: list[dict] = []
    defaults: list[dict] = []

    for entry in raw:
        k = entry.get("key")
        if not k:
            continue

        item = {
            "key": k,
            "label": entry.get("label", k.replace("_", " ").title()),
            "url":   entry.get("url", f"/api/ui/{k}/tab"),
            "icon":  entry.get("icon", "home"),
            "default": bool(entry.get("default", False)),
        }

        if item["default"]:
            defaults.append(item)

        items.append(item)

    if len(defaults) > 1:
        raise RuntimeError(
            f"Mehrere Default-Nav-Items gefunden: {[d['key'] for d in defaults]}"
        )

    return items
