"""Mask: selectively hide or partially reveal config values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class MaskError(Exception):
    pass


@dataclass
class MaskResult:
    masked: dict
    keys_masked: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.keys_masked)

    def summary(self) -> str:
        if not self.keys_masked:
            return "No keys masked."
        return f"Masked {self.count} key(s): {', '.join(self.keys_masked)}"


def _mask_value(value: Any, reveal_chars: int = 0) -> str:
    """Return a masked representation of a scalar value."""
    text = str(value)
    if reveal_chars <= 0 or reveal_chars >= len(text):
        return "***"
    return text[:reveal_chars] + "***"


def mask_keys(
    config: dict,
    keys: list[str],
    reveal_chars: int = 0,
    *,
    _prefix: str = "",
) -> MaskResult:
    """Recursively mask specified dot-notation keys in config."""
    if not isinstance(config, dict):
        raise MaskError("config must be a dict")

    result: dict = {}
    masked_keys: list[str] = []

    for k, v in config.items():
        full_key = f"{_prefix}{k}" if _prefix else k
        if full_key in keys:
            result[k] = _mask_value(v, reveal_chars)
            masked_keys.append(full_key)
        elif isinstance(v, dict):
            sub = mask_keys(v, keys, reveal_chars, _prefix=f"{full_key}.")
            result[k] = sub.masked
            masked_keys.extend(sub.keys_masked)
        else:
            result[k] = v

    return MaskResult(masked=result, keys_masked=masked_keys)


def mask_patch(patch: dict, keys: list[str], reveal_chars: int = 0) -> MaskResult:
    """Mask values in a patch dict for safe display."""
    if not isinstance(patch, dict):
        raise MaskError("patch must be a dict")
    return mask_keys(patch, keys, reveal_chars)
