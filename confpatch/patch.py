"""Core patch application logic for confpatch."""

from __future__ import annotations

from typing import Any


def load_patch(patch_data: dict) -> dict:
    """Validate and return a patch dict.

    A patch is a flat or nested dict where each key path maps to a new value.
    Dot-notation keys like 'database.host' are supported.
    """
    if not isinstance(patch_data, dict):
        raise TypeError(f"Patch must be a dict, got {type(patch_data).__name__}")
    return patch_data


def _set_nested(config: dict, key_path: str, value: Any) -> None:
    """Set a value in a nested dict using dot-notation key path."""
    keys = key_path.split(".")
    target = config
    for key in keys[:-1]:
        if key not in target or not isinstance(target[key], dict):
            target[key] = {}
        target = target[key]
    target[keys[-1]] = value


def apply_patch(config: dict, patch: dict, allow_new_keys: bool = True) -> dict:
    """Apply a patch dict to a config dict.

    Args:
        config: The original configuration dictionary.
        patch: A flat dict with dot-notation keys or nested dict values.
        allow_new_keys: If False, raise KeyError when patch introduces new keys.

    Returns:
        A new dict with the patch applied.
    """
    import copy

    result = copy.deepcopy(config)

    for key, value in patch.items():
        if not allow_new_keys:
            # Check top-level key exists
            top_key = key.split(".")[0]
            if top_key not in result:
                raise KeyError(f"Key '{top_key}' not found in config and allow_new_keys=False")
        _set_nested(result, key, value)

    return result
