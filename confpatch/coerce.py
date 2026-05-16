"""Type coercion utilities for config values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CoerceError(Exception):
    pass


SUPPORTED_TYPES = ("int", "float", "str", "bool", "list", "null")


@dataclass
class CoerceResult:
    original: dict
    coerced: dict
    changes: list[tuple[str, Any, Any]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "No values coerced."
        lines = [f"Coerced {self.count()} value(s):"]
        for key, old, new in self.changes:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _coerce_value(value: Any, target_type: str) -> Any:
    if target_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise CoerceError(f"Cannot coerce {value!r} to int: {e}")
    elif target_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise CoerceError(f"Cannot coerce {value!r} to float: {e}")
    elif target_type == "str":
        return str(value)
    elif target_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
        raise CoerceError(f"Cannot coerce {value!r} to bool")
    elif target_type == "list":
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        raise CoerceError(f"Cannot coerce {value!r} to list")
    elif target_type == "null":
        return None
    else:
        raise CoerceError(f"Unknown target type: {target_type!r}. Supported: {SUPPORTED_TYPES}")


def coerce_keys(config: dict, coercions: dict[str, str]) -> CoerceResult:
    """Apply type coercions to specified keys. coercions maps dot-path -> target_type."""
    import copy
    result = copy.deepcopy(config)
    changes: list[tuple[str, Any, Any]] = []

    for dot_path, target_type in coercions.items():
        parts = dot_path.split(".")
        node = result
        for part in parts[:-1]:
            if not isinstance(node, dict) or part not in node:
                raise CoerceError(f"Key path not found: {dot_path!r}")
            node = node[part]
        leaf = parts[-1]
        if not isinstance(node, dict) or leaf not in node:
            raise CoerceError(f"Key path not found: {dot_path!r}")
        old_val = node[leaf]
        new_val = _coerce_value(old_val, target_type)
        if new_val != old_val:
            changes.append((dot_path, old_val, new_val))
        node[leaf] = new_val

    return CoerceResult(original=config, coerced=result, changes=changes)
