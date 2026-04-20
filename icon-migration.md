# Plan: Alle Icons als SVG-Dateien in ui/icons/ (MDI)

## Kontext

Aktuell gibt es zwei parallele Icon-Systeme:
1. **Statisches Sprite** `icons.svg` — 35 hardcodierte Google-Material-Icons (viewBox `0 -960 960 960`), direkt per `{% include %}` in `_base.html` eingebunden
2. **Dynamisches Sprite** via `build_sprite()` in `icons.py` — liest SVG-Dateien aus `ui/icons/` (aktuell 4: moon, sun, circle, circle-outline), Ergebnis in `icon_sprite`-Global

Dazu: **133 inline SVGs** in Templates mit direkten Pfad-Definitionen (24×24, Stroke-Stil).

Ziel: Jedes Icon kommt als eigene `.svg`-Datei von **Pictogrammers MDI** (`viewBox="0 0 24 24"`) in `astrapi-core/astrapi_core/ui/icons/`. Das Sprite wird vollständig durch `build_sprite()` gebaut — kein hardcodiertes `icons.svg` mehr, keine wiederholten inline Pfade in Templates.

---

## Download-Quelle

**CDN:** `https://cdn.jsdelivr.net/npm/@mdi/svg@latest/svg/{mdi-name}.svg`

Alle Icons: `viewBox="0 0 24 24"`, kein explizites `fill`-Attribut (CSS-kompatibel).

---

## Kritische Dateien

| Datei | Rolle |
|---|---|
| `astrapi-core/astrapi_core/ui/icons/` | Zielordner für alle SVG-Dateien |
| `astrapi-core/astrapi_core/ui/icons.py` | `build_sprite()` + `_symbol()` — `<title>`-Tag → Icon-ID |
| `astrapi-core/astrapi_core/ui/app.py` | Ruft `build_sprite()` mit `extra_dirs=[..., ui/icons/]` auf |
| `astrapi-core/astrapi_core/ui/templates/_base.html` | `{% include "sprites/icons.svg" %}` entfernen |
| `astrapi-core/astrapi_core/ui/templates/partials/components/sprites/icons.svg` | Inhalt leeren (leeres `<svg>`) |
| `astrapi-core/astrapi_core/ui/templates/partials/components/ui_macros.html` | `icon()`-Makro + Button-Makros |
| `astrapi-core/astrapi_core/ui/templates/partials/list_wrapper_inner.html` | Inline menu-dots, Pagination-Pfeile |
| `astrapi-core/astrapi_core/modules/scheduler/templates/partials/list.html` | Inline play, edit, trash, clock |
| `astrapi-core/astrapi_core/ui/templates/partials/confirm_modal.html` | Inline X (close) |
| `astrapi-backup/astrapi_backup/modules/borg/templates/partials/browse.html` | Inline folder, file, download |

---

## Schritt 1: Download-Skript ausführen

Python-Skript einmalig aus dem Projektverzeichnis ausführen. Es lädt alle Icons herunter und fügt den `<title>`-Tag mit der gewünschten Icon-ID ein (damit `build_sprite()` die korrekten `#icon-{name}`-IDs erzeugt, unabhängig vom MDI-Dateinamen).

```python
import urllib.request, re
from pathlib import Path

BASE = "https://cdn.jsdelivr.net/npm/@mdi/svg@latest/svg/{mdi}.svg"
OUT  = Path("astrapi-core/astrapi_core/ui/icons")
OUT.mkdir(exist_ok=True)

# (icon-id, mdi-dateiname)
ICONS = [
    # Bestehende 35 Material-Icons ersetzen
    ("home",          "home"),
    ("settings",      "settings"),
    ("list",          "format-list-bulleted"),
    ("bar-chart",     "chart-bar"),
    ("chart",         "chart-bar"),          # Alias
    ("clock",         "clock-outline"),
    ("alert",         "alert"),
    ("monitor",       "monitor"),
    ("archive",       "inbox-arrow-down"),
    ("search",        "magnify"),
    ("edit",          "pencil"),
    ("trash",         "delete"),
    ("plus",          "plus"),
    ("minus",         "minus"),
    ("play",          "play"),
    ("play-debug",    "bug-play"),
    ("bug",           "bug"),
    ("terminal",      "console"),
    ("file-text",     "file-document"),
    ("external-link", "open-in-new"),
    ("eye",           "eye"),
    ("info",          "information"),
    ("shield",        "shield"),
    ("server",        "server"),
    ("database",      "database"),
    ("users",         "account-group"),
    ("calendar",      "calendar"),
    ("bell",          "bell"),
    ("refresh",       "refresh"),
    ("refresh-lg",    "refresh"),            # Alias
    ("hamburger",     "menu"),
    ("close",         "close"),
    ("power-on",      "power"),
    ("power-off",     "power-off"),
    # Neue Icons
    ("menu-dots",     "dots-vertical"),
    ("check",         "check"),
    ("chevron-left",  "chevron-left"),
    ("chevron-right", "chevron-right"),
    ("folder",        "folder"),
    ("file",          "file"),
    ("download",      "download"),
    ("arrow-up",      "arrow-up"),
]

for icon_id, mdi_name in ICONS:
    url  = BASE.format(mdi=mdi_name)
    dest = OUT / f"{icon_id}.svg"
    try:
        svg = urllib.request.urlopen(url).read().decode()
        # <title> mit Icon-ID direkt nach <svg ...> einfügen
        svg = re.sub(r"(<svg[^>]*>)", rf"\1<title>{icon_id}</title>", svg, count=1)
        dest.write_text(svg)
        print(f"✓ {icon_id} ({mdi_name})")
    except Exception as e:
        print(f"✗ {icon_id} ({mdi_name}): {e}")
```

---

## Schritt 2: `build_sprite()` — fill normalisieren

In `astrapi-core/astrapi_core/ui/icons.py`, Funktion `_symbol()`, nach dem `inner`-Parsing:

```python
# MDI-Icons haben kein explizites fill – sicherheitshalber normalisieren
inner = inner.replace('fill="black"', 'fill="currentColor"')
inner = inner.replace("fill='black'", "fill='currentColor'")
```

---

## Schritt 3: `icons.svg` leeren und `_base.html` bereinigen

**`icons.svg`:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true"></svg>
```

**`_base.html`:** Zeile entfernen:
```jinja2
{% include "partials/components/sprites/icons.svg" %}
```

---

## Schritt 4: Inline SVGs in Templates ersetzen

Priorität nach Häufigkeit:

| Template | Inline Icons ersetzen durch |
|---|---|
| `list_wrapper_inner.html` | `menu-dots` (×3), `chevron-left`, `chevron-right` |
| `scheduler/partials/list.html` | `play`, `edit`, `trash`, `clock` |
| `ui_macros.html` `status_inline()` | `check`, `alert`, `play`, `refresh` |
| `confirm_modal.html` | `close` |
| `borg/browse.html` | `folder`, `file`, `download`, `arrow-up` |

Ersetzungsmuster:
```html
<!-- vorher -->
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="..."/>
</svg>

<!-- nachher -->
<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none">
  <use href="#icon-edit"></use>
</svg>
```

Oder via bestehendem `icon()`-Makro aus `ui_macros.html`:
```jinja2
{{ icon('edit') }}
```

**Nicht ersetzen:** Spinner-SVGs mit `animation:spin` — bleiben inline.

---

## Verifikation

1. Download-Skript ausführen → alle `.svg`-Dateien in `ui/icons/` vorhanden
2. App starten → Browser-DevTools: alle `<symbol id="icon-*">` im DOM
3. Navigation, Buttons, Status-Badges — alle Icons sichtbar
4. Dark/Light-Mode umschalten → Icons passen Farbe an
5. Kein `{% include "sprites/icons.svg" %}` mehr aktiv
