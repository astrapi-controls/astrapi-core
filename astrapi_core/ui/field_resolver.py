"""Helpers for resolving dynamic field options before template rendering."""

from typing import Callable

# Registry: URL-Präfix → Funktion(endpoint: str) -> list[dict]
_options_fetchers: dict[str, Callable[[str], list]] = {}


def register_options_fetcher(prefix: str, fn: Callable[[str], list]) -> None:
    """Registriert eine Funktion zum Auflösen von options_endpoint-URLs.

    fn(endpoint: str) → list[{"value": ..., "label": ...}]
    Wird von Apps (z.B. astrapi-backup) aufgerufen, um app-spezifische
    Datenquellen bereitzustellen, ohne dass astrapi-core von der App abhängt.
    """
    _options_fetchers[prefix] = fn


def resolve_options_endpoint(fields: list) -> list:
    """Replaces options_endpoint with actual options fetched from the engine."""
    _cache = {}
    result = []
    for field in fields:
        endpoint = field.get("options_endpoint")
        if endpoint:
            if endpoint not in _cache:
                _cache[endpoint] = _fetch_options(endpoint)
            field = dict(field)
            field["options"] = _cache[endpoint]
            del field["options_endpoint"]
        result.append(field)
    return result


def _fetch_options(endpoint: str) -> list:
    for prefix, fn in _options_fetchers.items():
        if endpoint.startswith(prefix):
            return fn(endpoint)
    return []
