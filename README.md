# AstrapiFlaskUi

> Minimales Flask-UI-Framework mit HTMX, Alpine.js und Dark/Light Mode.  
> Designed für schnelle Inhouse-Tools und Admin-UIs.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Schnellstart

```bash
git clone https://gitlab.com/<dein-user>/AstrapiFlaskUi.git myproject
cd myproject
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
# → http://localhost:5000
```

---

## Projektstruktur

```
AstrapiFlaskUi/
│
├── core/                          # ⚙️  Framework-Kern – NICHT manuell ändern
│   ├── static/
│   │   ├── css/app.css            # Design-System (Dark/Light, alle Komponenten)
│   │   └── js/
│   │       ├── app.js             # Dark Mode + Active-Nav
│   │       └── components/
│   │           └── navigation.js  # Mobile Sidebar
│   ├── templates/
│   │   ├── base.html              # HTML-Grundgerüst
│   │   ├── index.html             # App-Shell (Sidebar + HTMX-Content)
│   │   ├── navigation/
│   │   │   └── index.html         # Sidebar mit Icon-Makros
│   │   └── partials/
│   │       └── tab_wrapper.html   # HTMX-Tab-Wrapper
│   └── ui/
│       ├── app.py                 # Flask App-Factory
│       ├── navigation.py          # items.yaml einlesen
│       └── page_factory.py        # Routen automatisch registrieren
│
├── app/                           # 🎨  Dein Projekt – hier arbeitest du
│   ├── config.py                  # APP_NAME, APP_VERSION, APP_LOGO_SVG …
│   ├── static/                    # Projektspezifische Assets (überschreibt core)
│   └── templates/
│       ├── navigation/
│       │   └── items.yaml         # ← Nav-Einträge hier pflegen
│       └── partials/
│           └── lists/
│               ├── overview.html  # Beispielseite 1: Karten-Grid
│               └── settings.html  # Beispielseite 2: Formular
│
├── main.py                        # Einstiegspunkt
├── requirements.txt
├── .env.example
├── .gitignore
├── CHANGELOG.md
└── README.md
```

---

## Neue Seite hinzufügen

**1. Eintrag in `app/templates/navigation/items.yaml`:**

```yaml
- key: meine_seite
  label: Meine Seite
  url: /api/ui/meine_seite/tab
  icon: list          # Verfügbare Icons unten
```

**2. Partial anlegen unter `app/templates/partials/lists/meine_seite.html`:**

```html
<div class="page-header">
  <span class="page-title">Meine Seite</span>
</div>

<div class="ds-list-grid">
  <!-- Inhalte hier -->
</div>
```

Das war's. `register_pages()` generiert die Flask-Routen automatisch.

---

## App anpassen

**`app/config.py`** – Name, Version, Logo:

```python
APP_NAME    = "myproject"
APP_VERSION = "1.0.0"
APP_LOGO_SVG = '<svg width="18" height="18" ...>...</svg>'
```

**Core-Template überschreiben** (selten nötig):  
Datei mit gleichem Pfad in `app/templates/` anlegen → hat Vorrang vor `core/templates/`.

**Eigene CSS/JS**:  
Dateien in `app/static/` ablegen und in `base.html` via `{% block extra_css %}` / `{% block extra_js %}` einbinden.

---

## Verfügbare Icons

| Name | Verwendung |
|------|-----------|
| `home` | Startseite |
| `list` | Listen-Ansicht |
| `chart` | Statistiken / Graphen |
| `clock` | Zeitplanung |
| `alert` | Warnungen / Fehler |
| `settings` | Konfiguration |
| `database` | Datenbank |
| `users` | Benutzer |
| `server` | Server / Hosts |
| `shield` | Sicherheit |

Neues Icon hinzufügen: SVG-Block in `core/templates/navigation/index.html` im `svg_icon`-Makro ergänzen.

---

## CSS-Komponenten (Kurzreferenz)

### Layout
| Klasse | Zweck |
|--------|-------|
| `app-layout` | Flex-Wrapper (Sidebar + Content) |
| `main-content` | Scrollbarer Content-Bereich |
| `page-header` | Titelzeile mit optionalem Button |
| `page-title` | Seitentitel |
| `ds-list-grid` | 2-Spalten-Grid für Karten |

### Karten
| Klasse | Zweck |
|--------|-------|
| `ds-card on` | Aktive Karte |
| `ds-card off` | Inaktive / deaktivierte Karte |
| `card-header` | Kopfzeile mit Titel |
| `card-inner` | Body-Bereich (flex) |
| `card-body` | Inhalt links |
| `card-actions` | Icon-Buttons rechts |
| `card-footer` | Fußzeile |
| `meta-grid` | Schlüssel-Wert-Raster (Monospace) |

### Buttons
| Klasse | Zweck |
|--------|-------|
| `btn btn-primary` | Primärer Button (blau) |
| `btn btn-ghost` | Transparenter Button |
| `btn btn-danger` | Gefahren-Button (rot) |
| `btn btn-sm` | Klein |
| `btn-icon` | Quadratischer Icon-Button |
| `btn-icon-run` | Grün (Ausführen) |
| `btn-icon-danger` | Rot (Löschen) |

### Formulare
| Klasse | Zweck |
|--------|-------|
| `form-group` | Wrapper für Label + Input |
| `form-label` | Beschriftung |
| `form-input` | Text-Input |
| `form-select` | Dropdown |
| `form-checkbox` | Checkbox |
| `required-mark` | Roter Stern `*` |

### Sonstiges
| Klasse | Zweck |
|--------|-------|
| `toggle-switch toggle-on/off` | Toggle-Schalter |
| `empty-state` | Leerer-Zustand-Platzhalter |
| `run-badge` | Pulsierendes "läuft"-Badge |

---

## Framework updaten

Der `core/`-Ordner ist das Framework – **nie manuell bearbeiten**.  
Eigener Code liegt ausschließlich in `app/`.

### Per Release-ZIP (empfohlen)

```bash
# ZIP von GitLab Releases herunterladen, dann:
cp -r AstrapiFlaskUi-core/core/ /pfad/zu/meinprojekt/
```

### Per git remote

```bash
git remote add upstream https://gitlab.com/<dein-user>/AstrapiFlaskUi.git
git fetch upstream
git checkout upstream/main -- core/
git commit -m "chore: update AstrapiFlaskUi core to vX.Y.Z"
```

Vollständige Anleitung: siehe [INSTALL.md](INSTALL.md)

**Was nie im `core/` landen sollte:**
- Projektspezifische Seiten
- Eigene Konfiguration
- Business-Logik

---

## Tech-Stack

| Library | Version | Zweck |
|---------|---------|-------|
| [Flask](https://flask.palletsprojects.com/) | 3.x | Backend / Routing |
| [HTMX](https://htmx.org/) | 1.9 | Dynamisches HTML ohne JS-Bundle |
| [Alpine.js](https://alpinejs.dev/) | 3.x | Reaktivität im Template |
| [Inter](https://rsms.me/inter/) | – | UI-Schrift |
| [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | – | Mono-Schrift für Meta-Daten |

---

## Lizenz

MIT – siehe [LICENSE](LICENSE)
