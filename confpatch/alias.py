"""Alias support: map short names to patch file paths."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class AliasError(Exception):
    pass


@dataclass
class AliasStore:
    aliases: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(self.aliases)

    @classmethod
    def from_dict(cls, data: dict) -> "AliasStore":
        return cls(aliases={str(k): str(v) for k, v in data.items()})


def _alias_path(config_path: Path) -> Path:
    return config_path.parent / f".{config_path.stem}_aliases.json"


def load_aliases(config_path: Path) -> AliasStore:
    path = _alias_path(config_path)
    if not path.exists():
        return AliasStore()
    try:
        data = json.loads(path.read_text())
        return AliasStore.from_dict(data)
    except Exception as exc:
        raise AliasError(f"Failed to load aliases: {exc}") from exc


def save_aliases(config_path: Path, store: AliasStore) -> None:
    path = _alias_path(config_path)
    try:
        path.write_text(json.dumps(store.to_dict(), indent=2))
    except Exception as exc:
        raise AliasError(f"Failed to save aliases: {exc}") from exc


def add_alias(config_path: Path, name: str, patch_path: str) -> AliasStore:
    if not name.strip():
        raise AliasError("Alias name must not be empty.")
    store = load_aliases(config_path)
    store.aliases[name] = patch_path
    save_aliases(config_path, store)
    return store


def remove_alias(config_path: Path, name: str) -> AliasStore:
    store = load_aliases(config_path)
    if name not in store.aliases:
        raise AliasError(f"Alias '{name}' not found.")
    del store.aliases[name]
    save_aliases(config_path, store)
    return store


def resolve_alias(config_path: Path, name: str) -> str:
    store = load_aliases(config_path)
    if name not in store.aliases:
        raise AliasError(f"Alias '{name}' is not defined.")
    return store.aliases[name]


def list_aliases(config_path: Path) -> List[tuple]:
    store = load_aliases(config_path)
    return sorted(store.aliases.items())
