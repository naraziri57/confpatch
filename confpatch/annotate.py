"""Annotation support: attach comments/notes to config keys."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


class AnnotateError(Exception):
    pass


@dataclass
class Annotation:
    key: str
    note: str
    author: str = "unknown"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "note": self.note,
            "author": self.author,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        return cls(
            key=data["key"],
            note=data["note"],
            author=data.get("author", "unknown"),
            tags=data.get("tags", []),
        )


def _annotations_path(config_path: Path) -> Path:
    return config_path.parent / f".{config_path.name}.annotations.json"


def load_annotations(config_path: Path) -> Dict[str, Annotation]:
    path = _annotations_path(config_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return {k: Annotation.from_dict(v) for k, v in data.items()}
    except Exception as exc:
        raise AnnotateError(f"Failed to load annotations: {exc}") from exc


def save_annotations(config_path: Path, annotations: Dict[str, Annotation]) -> None:
    path = _annotations_path(config_path)
    try:
        path.write_text(json.dumps({k: v.to_dict() for k, v in annotations.items()}, indent=2))
    except Exception as exc:
        raise AnnotateError(f"Failed to save annotations: {exc}") from exc


def add_annotation(config_path: Path, key: str, note: str, author: str = "unknown", tags: List[str] | None = None) -> Annotation:
    if not key.strip():
        raise AnnotateError("Key must not be empty.")
    if not note.strip():
        raise AnnotateError("Note must not be empty.")
    annotations = load_annotations(config_path)
    ann = Annotation(key=key, note=note, author=author, tags=tags or [])
    annotations[key] = ann
    save_annotations(config_path, annotations)
    return ann


def remove_annotation(config_path: Path, key: str) -> None:
    annotations = load_annotations(config_path)
    if key not in annotations:
        raise AnnotateError(f"No annotation found for key: {key!r}")
    del annotations[key]
    save_annotations(config_path, annotations)


def get_annotation(config_path: Path, key: str) -> Annotation:
    annotations = load_annotations(config_path)
    if key not in annotations:
        raise AnnotateError(f"No annotation found for key: {key!r}")
    return annotations[key]
