"""Environment variable injection for confpatch patches.

Allows patch values to reference environment variables using ${ENV_VAR} syntax.
"""

import os
import re
from typing import Any

ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class EnvError(Exception):
    """Raised when an environment variable is missing or injection fails."""


def _inject_string(value: str, strict: bool = True) -> str:
    """Replace ${VAR} placeholders in a string with environment variable values."""
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        env_val = os.environ.get(var_name)
        if env_val is None:
            if strict:
                raise EnvError(
                    f"Environment variable '{var_name}' is not set."
                )
            return match.group(0)  # leave placeholder as-is
        return env_val

    return ENV_PATTERN.sub(replacer, value)


def inject_env(value: Any, strict: bool = True) -> Any:
    """Recursively inject environment variables into patch values.

    Supports strings, dicts, and lists. Non-string scalars are returned as-is.

    Args:
        value: The patch value (or nested structure) to process.
        strict: If True, raise EnvError for missing variables.
                If False, leave unresolved placeholders in place.

    Returns:
        The value with environment variables substituted.
    """
    if isinstance(value, str):
        return _inject_string(value, strict=strict)
    if isinstance(value, dict):
        return {k: inject_env(v, strict=strict) for k, v in value.items()}
    if isinstance(value, list):
        return [inject_env(item, strict=strict) for item in value]
    return value


def inject_patch_env(patch: dict, strict: bool = True) -> dict:
    """Apply environment variable injection to all values in a patch dict.

    Args:
        patch: The patch dictionary to process.
        strict: Whether to raise on missing env vars.

    Returns:
        A new patch dict with env vars resolved.
    """
    if not isinstance(patch, dict):
        raise EnvError("Patch must be a dictionary.")
    return {key: inject_env(val, strict=strict) for key, val in patch.items()}
