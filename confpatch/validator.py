"""Validation utilities for patch files and config structures."""

from typing import Any


class PatchValidationError(ValueError):
    """Raised when a patch file fails validation."""
    pass


SUPPORTED_FORMATS = ("yaml", "toml")


def validate_patch_structure(patch: Any) -> None:
    """Validate that a patch is a non-empty dict.

    Args:
        patch: The loaded patch object to validate.

    Raises:
        PatchValidationError: If the patch is not a dict or is empty.
    """
    if not isinstance(patch, dict):
        raise PatchValidationError(
            f"Patch must be a mapping (dict), got {type(patch).__name__}"
        )
    if len(patch) == 0:
        raise PatchValidationError("Patch must not be empty")


def validate_keys(patch: dict, *, allow_dot_notation: bool = True) -> None:
    """Validate that all keys in the patch are strings.

    Args:
        patch: The patch dict to validate.
        allow_dot_notation: Whether dot-notation keys are permitted.

    Raises:
        PatchValidationError: If any key is not a string or contains
            invalid characters.
    """
    for key in patch:
        if not isinstance(key, str):
            raise PatchValidationError(
                f"All patch keys must be strings, got key {key!r} of type {type(key).__name__}"
            )
        if not allow_dot_notation and "." in key:
            raise PatchValidationError(
                f"Dot-notation keys are not allowed, but found key {key!r}"
            )
        if key.strip() == "":
            raise PatchValidationError("Patch keys must not be empty or whitespace")


def validate_format(fmt: str) -> None:
    """Check that the requested format is supported.

    Args:
        fmt: Format string, e.g. 'yaml' or 'toml'.

    Raises:
        PatchValidationError: If the format is not supported.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise PatchValidationError(
            f"Unsupported format {fmt!r}. Choose one of: {', '.join(SUPPORTED_FORMATS)}"
        )
