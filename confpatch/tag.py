"""Tag-based patch grouping and filtering for confpatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json


class TagError(Exception):
    """Raised when a tagging operation fails."""


@dataclass
class TagStore:
    tags: Dict[str, List[str]] = field(default_factory=dict)  # tag -> [patch_paths]

    def to_dict(self) -> dict:
        return {"tags": self.tags}

    @classmethod
    def from_dict(cls, data: dict) -> "TagStore":
        return cls(tags=data.get("tags", {}))


def _tag_path(config_file: Path) -> Path:
    return config_file.parent / f".{config_file.stem}_tags.json"


def load_tags(config_file: Path) -> TagStore:
    path = _tag_path(config_file)
    if not path.exists():
        return TagStore()
    try:
        data = json.loads(path.read_text())
        return TagStore.from_dict(data)
    except Exception as exc:
        raise TagError(f"Failed to load tags: {exc}") from exc


def save_tags(config_file: Path, store: TagStore) -> None:
    path = _tag_path(config_file)
    try:
        path.write_text(json.dumps(store.to_dict(), indent=2))
    except Exception as exc:
        raise TagError(f"Failed to save tags: {exc}") from exc


def add_tag(config_file: Path, tag: str, patch_path: str) -> TagStore:
    store = load_tags(config_file)
    store.tags.setdefault(tag, [])
    if patch_path not in store.tags[tag]:
        store.tags[tag].append(patch_path)
    save_tags(config_file, store)
    return store


def remove_tag(config_file: Path, tag: str, patch_path: Optional[str] = None) -> TagStore:
    store = load_tags(config_file)
    if tag not in store.tags:
        raise TagError(f"Tag '{tag}' not found.")
    if patch_path is None:
        del store.tags[tag]
    else:
        try:
            store.tags[tag].remove(patch_path)
        except ValueError:
            raise TagError(f"Patch '{patch_path}' not found under tag '{tag}'.")
        if not store.tags[tag]:
            del store.tags[tag]
    save_tags(config_file, store)
    return store


def get_patches_for_tag(config_file: Path, tag: str) -> List[str]:
    store = load_tags(config_file)
    if tag not in store.tags:
        raise TagError(f"Tag '{tag}' not found.")
    return list(store.tags[tag])


def list_tags(config_file: Path) -> List[str]:
    store = load_tags(config_file)
    return sorted(store.tags.keys())
