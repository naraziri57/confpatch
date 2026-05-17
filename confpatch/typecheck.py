"""Type checking utilities for config values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


class TypeCheckError(Exception):
    pass


@dataclass
class TypeCheckResult:
    violations: list[dict[str, Any]] = field(default_factory=list)

    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def count(self) -> int:
        return len(self.violations)

    def summary(self) -> str:
        if not self.has_violations():
            return "No type violations found."
        lines = [f"{len(self.violations)} type violation(s) found:"]
        for v in self.violations:
            lines.append(
                f"  {v['key']}: expected {v['expected']}, got {v['actual']} ({v['value']!r})"
            )
        return "\n".join(lines)


def _get_nested(config: dict, key: str) -> Any:
    parts = key.split(".")
    current: Any = config
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise TypeCheckError(f"Key not found: {key!r}")
        current = current[part]
    return current


def check_types(config: dict, schema: dict[str, str]) -> TypeCheckResult:
    """Check config values against a flat key->type schema.

    Args:
        config: The loaded config dict.
        schema: Mapping of dot-notation keys to expected type names.

    Returns:
        TypeCheckResult with any violations found.
    """
    if not isinstance(config, dict):
        raise TypeCheckError("config must be a dict")
    if not isinstance(schema, dict):
        raise TypeCheckError("schema must be a dict")

    violations: list[dict[str, Any]] = []

    for key, type_name in schema.items():
        if type_name not in TYPE_MAP:
            raise TypeCheckError(
                f"Unknown type {type_name!r} for key {key!r}. "
                f"Valid types: {list(TYPE_MAP)}"
            )
        expected_type = TYPE_MAP[type_name]
        try:
            value = _get_nested(config, key)
        except TypeCheckError:
            violations.append(
                {
                    "key": key,
                    "expected": type_name,
                    "actual": "missing",
                    "value": None,
                }
            )
            continue

        if not isinstance(value, expected_type):
            violations.append(
                {
                    "key": key,
                    "expected": type_name,
                    "actual": type(value).__name__,
                    "value": value,
                }
            )

    return TypeCheckResult(violations=violations)
