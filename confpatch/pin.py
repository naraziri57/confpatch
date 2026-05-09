"""Pin specific config keys to prevent them from being overwritten by patches."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


class PinError(Exception):
    pass


@dataclass
class PinStore:
    pinned: set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {"pinned": sorted(self.pinned)}

    @classmethod
    def from_dict(cls, data: dict) -> "PinStore":
        return cls(pinned=set(data.get("pinned", [])))


def _pin_path(config_path: Path) -> Path:
    return config_path.parent / (config_path.name + ".pins")


def load_pins(config_path: Path) -> PinStore:
    """Load pinned keys for a given config file."""
    path = _pin_path(config_path)
    if not path.exists():
        return PinStore()
    try:
        data = json.loads(path.read_text())
        return PinStore.from_dict(data)
    except Exception as e:
        raise PinError(f"Failed to load pins from {path}: {e}") from e


def save_pins(config_path: Path, store: PinStore) -> None:
    """Persist pinned keys for a given config file."""
    path = _pin_path(config_path)
    try:
        path.write_text(json.dumps(store.to_dict(), indent=2))
    except Exception as e:
        raise PinError(f"Failed to save pins to {path}: {e}") from e


def pin_key(config_path: Path, key: str) -> PinStore:
    """Add a key to the pin list."""
    store = load_pins(config_path)
    store.pinned.add(key)
    save_pins(config_path, store)
    return store


def unpin_key(config_path: Path, key: str) -> PinStore:
    """Remove a key from the pin list."""
    store = load_pins(config_path)
    store.pinned.discard(key)
    save_pins(config_path, store)
    return store


def filter_pinned(patch: dict[str, Any], store: PinStore) -> tuple[dict[str, Any], list[str]]:
    """Return a copy of patch with pinned keys removed, plus list of skipped keys."""
    skipped = [k for k in patch if k in store.pinned]
    filtered = {k: v for k, v in patch.items() if k not in store.pinned}
    return filtered, skipped
