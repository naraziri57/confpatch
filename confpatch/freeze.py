"""Freeze/unfreeze keys in a config to prevent them from being overwritten by patches."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class FreezeError(Exception):
    pass


@dataclass
class FreezeStore:
    config_path: Path
    frozen_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"config": str(self.config_path), "frozen": self.frozen_keys}

    @classmethod
    def from_dict(cls, data: dict) -> "FreezeStore":
        return cls(
            config_path=Path(data["config"]),
            frozen_keys=data.get("frozen", []),
        )


def _freeze_path(config_path: Path) -> Path:
    return config_path.parent / f".{config_path.stem}.freeze.json"


def load_freeze_store(config_path: Path) -> FreezeStore:
    fp = _freeze_path(config_path)
    if not fp.exists():
        return FreezeStore(config_path=config_path)
    try:
        data = json.loads(fp.read_text())
        return FreezeStore.from_dict(data)
    except Exception as e:
        raise FreezeError(f"Failed to load freeze store: {e}") from e


def save_freeze_store(store: FreezeStore) -> None:
    fp = _freeze_path(store.config_path)
    try:
        fp.write_text(json.dumps(store.to_dict(), indent=2))
    except Exception as e:
        raise FreezeError(f"Failed to save freeze store: {e}") from e


def freeze_key(config_path: Path, key: str) -> FreezeStore:
    if not config_path.exists():
        raise FreezeError(f"Config file not found: {config_path}")
    store = load_freeze_store(config_path)
    if key not in store.frozen_keys:
        store.frozen_keys.append(key)
        save_freeze_store(store)
    return store


def unfreeze_key(config_path: Path, key: str) -> FreezeStore:
    store = load_freeze_store(config_path)
    if key not in store.frozen_keys:
        raise FreezeError(f"Key '{key}' is not frozen")
    store.frozen_keys.remove(key)
    save_freeze_store(store)
    return store


def filter_frozen_keys(patch: dict[str, Any], store: FreezeStore) -> tuple[dict[str, Any], list[str]]:
    """Return (filtered_patch, skipped_keys) removing any frozen keys from patch."""
    skipped: list[str] = []
    filtered: dict[str, Any] = {}
    for k, v in patch.items():
        if k in store.frozen_keys:
            skipped.append(k)
        else:
            filtered[k] = v
    return filtered, skipped
