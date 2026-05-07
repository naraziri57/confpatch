"""Named patch profiles — save and apply named sets of patches."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ProfileError(Exception):
    pass


@dataclass
class Profile:
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
    def from_dict(cls, data: dict) -> "Profile":
        return cls(
            name=data["name"],
            patch=data["patch"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def _profiles_path(store_dir: Path) -> Path:
    return store_dir / "profiles.json"


def load_profiles(store_dir: Path) -> list[Profile]:
    path = _profiles_path(store_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return [Profile.from_dict(p) for p in data]
    except Exception as exc:
        raise ProfileError(f"Failed to load profiles: {exc}") from exc


def save_profile(profile: Profile, store_dir: Path) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    profiles = load_profiles(store_dir)
    profiles = [p for p in profiles if p.name != profile.name]
    profiles.append(profile)
    path = _profiles_path(store_dir)
    try:
        path.write_text(json.dumps([p.to_dict() for p in profiles], indent=2))
    except Exception as exc:
        raise ProfileError(f"Failed to save profile: {exc}") from exc


def get_profile(name: str, store_dir: Path) -> Profile:
    profiles = load_profiles(store_dir)
    for p in profiles:
        if p.name == name:
            return p
    raise ProfileError(f"Profile '{name}' not found")


def delete_profile(name: str, store_dir: Path) -> None:
    profiles = load_profiles(store_dir)
    updated = [p for p in profiles if p.name != name]
    if len(updated) == len(profiles):
        raise ProfileError(f"Profile '{name}' not found")
    path = _profiles_path(store_dir)
    path.write_text(json.dumps([p.to_dict() for p in updated], indent=2))
