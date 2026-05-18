"""Replace placeholder tokens in config values with resolved values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

PLACEHOLDER_RE = re.compile(r"<([^>]+)>")


class PlaceholderError(Exception):
    pass


@dataclass
class PlaceholderResult:
    original: dict
    resolved: dict
    replacements: list[tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)

    def has_changes(self) -> bool:
        return len(self.replacements) > 0

    def count(self) -> int:
        return len(self.replacements)

    def summary(self) -> str:
        if not self.has_changes():
            return "No placeholder replacements made."
        lines = [f"Replaced {self.count()} placeholder(s):"]
        for key, old, new in self.replacements:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _resolve_string(value: str, mapping: dict[str, str], strict: bool) -> str:
    def replace(m: re.Match) -> str:
        token = m.group(1).strip()
        if token not in mapping:
            if strict:
                raise PlaceholderError(f"No value provided for placeholder: <{token}>")
            return m.group(0)
        return str(mapping[token])

    return PLACEHOLDER_RE.sub(replace, value)


def _resolve_value(value: Any, mapping: dict[str, str], strict: bool) -> Any:
    if isinstance(value, str):
        return _resolve_string(value, mapping, strict)
    if isinstance(value, dict):
        return {k: _resolve_value(v, mapping, strict) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_value(item, mapping, strict) for item in value]
    return value


def resolve_placeholders(
    config: dict,
    mapping: dict[str, str],
    keys: list[str] | None = None,
    strict: bool = True,
) -> PlaceholderResult:
    """Replace <token> placeholders in config values using mapping.

    Args:
        config: The config dict to process.
        mapping: Token -> replacement value.
        keys: If provided, only process these top-level keys.
        strict: If True, raise on unresolved placeholders.
    """
    if not isinstance(config, dict):
        raise PlaceholderError("Config must be a dict.")

    resolved = dict(config)
    replacements: list[tuple[str, str, str]] = []

    target_keys = keys if keys is not None else list(config.keys())

    for k in target_keys:
        if k not in config:
            continue
        old_val = config[k]
        new_val = _resolve_value(old_val, mapping, strict)
        resolved[k] = new_val
        if new_val != old_val:
            replacements.append((k, str(old_val), str(new_val)))

    return PlaceholderResult(
        original=config,
        resolved=resolved,
        replacements=replacements,
    )
