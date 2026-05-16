"""Preset management: save and apply named patch presets."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PresetError(Exception):
    pass


@dataclass
class Preset:
    name: str
    patch: dict[str, Any]
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "patch": self.patch,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        return cls(
            name=data["name"],
            patch=data["patch"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def _preset_path(config_path: Path) -> Path:
    return config_path.parent / f".{config_path.stem}_presets.json"


def load_presets(config_path: Path) -> dict[str, Preset]:
    path = _preset_path(config_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return {name: Preset.from_dict(entry) for name, entry in data.items()}
    except Exception as e:
        raise PresetError(f"Failed to load presets: {e}") from e


def save_preset(config_path: Path, preset: Preset) -> Preset:
    if not preset.name or not preset.name.strip():
        raise PresetError("Preset name must not be empty.")
    if not isinstance(preset.patch, dict):
        raise PresetError("Preset patch must be a dict.")
    presets = load_presets(config_path)
    presets[preset.name] = preset
    path = _preset_path(config_path)
    path.write_text(json.dumps({k: v.to_dict() for k, v in presets.items()}, indent=2))
    return preset


def delete_preset(config_path: Path, name: str) -> None:
    presets = load_presets(config_path)
    if name not in presets:
        raise PresetError(f"Preset '{name}' not found.")
    del presets[name]
    path = _preset_path(config_path)
    path.write_text(json.dumps({k: v.to_dict() for k, v in presets.items()}, indent=2))


def get_preset(config_path: Path, name: str) -> Preset:
    presets = load_presets(config_path)
    if name not in presets:
        raise PresetError(f"Preset '{name}' not found.")
    return presets[name]
