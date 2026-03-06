"""app/modules/hosts/storage.py – Storage-Instanz für das Hosts-Modul.

Verwendet die zentrale YamlStorage-Klasse aus dem Framework.
Daten liegen in app/data/hosts.yaml (app-weit zugänglich).

Schreibzugriff nur über die API-Endpunkte in api.py.
"""
from core.ui.storage import YamlStorage
import yaml
from pathlib import Path

# Seed-Daten aus der lokalen hosts.yaml laden (nur beim ersten Start)
_seed_file = Path(__file__).resolve().parent / "data" / "hosts.yaml"
_seed = {}
if _seed_file.exists():
    with open(_seed_file, encoding="utf-8") as f:
        _seed = yaml.safe_load(f) or {}

store = YamlStorage("hosts", seed_data=_seed)
