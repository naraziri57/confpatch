"""Extract specific keys or subtrees from a config into a new file."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from confpatch.loaders import load_config, save_config


class ExtractError(Exception):
    pass


@dataclass
class ExtractResult:
    source: str
    keys: list[str]
    extracted: dict[str, Any] = field(default_factory=dict)

    def has_data(self) -> bool:
        return bool(self.extracted)

    def count(self) -> int:
        return len(self.extracted)

    def summary(self) -> str:
        if not self.has_data():
            return f"No keys extracted from {self.source}"
        return f"Extracted {self.count()} key(s) from {self.source}: {', '.join(self.extracted)}"


def _get_nested(config: dict, key: str) -> Any:
    """Resolve a dot-notation key from a nested dict."""
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise ExtractError(f"Key not found: {key!r}")
        node = node[part]
    return node


def extract_keys(
    config: dict[str, Any],
    keys: list[str],
) -> dict[str, Any]:
    """Extract the given dot-notation keys from config into a flat dict."""
    if not isinstance(config, dict):
        raise ExtractError("Config must be a dict")
    result: dict[str, Any] = {}
    for key in keys:
        result[key] = _get_nested(config, key)
    return result


def extract_from_file(
    source: str,
    keys: list[str],
    dest: str | None = None,
    fmt: str | None = None,
    dry_run: bool = False,
) -> ExtractResult:
    """Load source config, extract keys, optionally save to dest."""
    config = load_config(source, fmt=fmt)
    extracted = extract_keys(config, keys)
    result = ExtractResult(source=source, keys=keys, extracted=extracted)
    if dest and not dry_run:
        save_config(extracted, dest, fmt=fmt)
    return result
