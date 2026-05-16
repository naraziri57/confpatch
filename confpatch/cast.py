"""Type casting utilities for config values with path targeting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CAST_TYPES = ("int", "float", "str", "bool")


class CastError(Exception):
    pass


@dataclass
class CastResult:
    config: dict
    changes: list[tuple[str, Any, Any]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "No values cast."
        lines = [f"Cast {len(self.changes)} value(s):"]
        for path, old, new in self.changes:
            lines.append(f"  {path}: {old!r} ({type(old).__name__}) -> {new!r} ({type(new).__name__})")
        return "\n".join(lines)


def _cast_value(value: Any, to_type: str) -> Any:
    if to_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise CastError(f"Cannot cast {value!r} to int: {e}") from e
    elif to_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise CastError(f"Cannot cast {value!r} to float: {e}") from e
    elif to_type == "str":
        return str(value)
    elif to_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
            raise CastError(f"Cannot cast string {value!r} to bool")
        return bool(value)
    else:
        raise CastError(f"Unknown type {to_type!r}. Choose from: {CAST_TYPES}")


def cast_key(config: dict, key_path: str, to_type: str, sep: str = ".") -> CastResult:
    """Cast the value at key_path to the given type. Returns a new config."""
    if to_type not in CAST_TYPES:
        raise CastError(f"Unknown type {to_type!r}. Choose from: {CAST_TYPES}")

    parts = key_path.split(sep)
    result = {k: v for k, v in config.items()}

    node = result
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            raise CastError(f"Key path {key_path!r} not found in config")
        node[part] = dict(node[part])
        node = node[part]

    leaf = parts[-1]
    if leaf not in node:
        raise CastError(f"Key {leaf!r} not found at path {key_path!r}")

    old_val = node[leaf]
    new_val = _cast_value(old_val, to_type)
    node[leaf] = new_val

    changes = [(key_path, old_val, new_val)] if old_val != new_val or type(old_val) != type(new_val) else []
    return CastResult(config=result, changes=changes)
