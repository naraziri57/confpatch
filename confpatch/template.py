"""Template variable substitution for patch files."""

import re
from typing import Any


class TemplateError(Exception):
    """Raised when template rendering fails."""


_VAR_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_value(value: Any, variables: dict) -> Any:
    """Recursively render template variables in a value."""
    if isinstance(value, str):
        return _render_string(value, variables)
    if isinstance(value, dict):
        return {k: render_value(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [render_value(item, variables) for item in value]
    return value


def _render_string(text: str, variables: dict) -> str:
    """Replace {{ var }} placeholders in a string."""
    def replacer(match):
        key = match.group(1)
        if key not in variables:
            raise TemplateError(f"Undefined template variable: '{key}'")
        return str(variables[key])

    return _VAR_PATTERN.sub(replacer, text)


def render_patch(patch: dict, variables: dict) -> dict:
    """Render all template variables in a patch dict.

    Args:
        patch: The patch dict, possibly containing {{ var }} placeholders.
        variables: Mapping of variable names to values.

    Returns:
        A new patch dict with all placeholders replaced.

    Raises:
        TemplateError: If a referenced variable is not defined.
    """
    if not isinstance(patch, dict):
        raise TemplateError("Patch must be a dict")
    return render_value(patch, variables)


def extract_variables(patch: dict) -> list[str]:
    """Return a sorted list of all template variable names used in a patch."""
    found: set[str] = set()
    _collect_vars(patch, found)
    return sorted(found)


def _collect_vars(value: Any, found: set) -> None:
    if isinstance(value, str):
        for match in _VAR_PATTERN.finditer(value):
            found.add(match.group(1))
    elif isinstance(value, dict):
        for v in value.values():
            _collect_vars(v, found)
    elif isinstance(value, list):
        for item in value:
            _collect_vars(item, found)
