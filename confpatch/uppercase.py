from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class UppercaseError(Exception):
    pass


@dataclass
class UppercaseResult:
    changed: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)

    def has_changes(self) -> bool:
        return len(self.changed) > 0

    def count(self) -> int:
        return len(self.changed)

    def summary(self) -> str:
        if not self.has_changes():
            return "No string values uppercased."
        return f"Uppercased {self.count()} value(s): {', '.join(self.changed)}"


def _uppercase_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.upper()
    return value


def uppercase_keys(
    config: dict,
    keys: list[str],
    *,
    nested_sep: str = ".",
) -> UppercaseResult:
    """Uppercase string values at the given dot-notation keys."""
    if not isinstance(config, dict):
        raise UppercaseError("Config must be a dict.")

    import copy
    result_config = copy.deepcopy(config)
    changed: list[str] = []

    for key in keys:
        parts = key.split(nested_sep)
        node = result_config
        try:
            for part in parts[:-1]:
                if not isinstance(node, dict) or part not in node:
                    raise UppercaseError(f"Key not found: {key!r}")
                node = node[part]
            leaf = parts[-1]
            if not isinstance(node, dict) or leaf not in node:
                raise UppercaseError(f"Key not found: {key!r}")
            original = node[leaf]
            updated = _uppercase_value(original)
            if updated != original:
                node[leaf] = updated
                changed.append(key)
        except UppercaseError:
            raise
        except Exception as exc:
            raise UppercaseError(f"Failed to uppercase key {key!r}: {exc}") from exc

    return UppercaseResult(changed=changed, config=result_config)
