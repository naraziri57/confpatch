"""Value transformation utilities for confpatch."""

from typing import Any, Callable, Dict


class TransformError(Exception):
    pass


_TRANSFORMS: Dict[str, Callable[[Any], Any]] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": lambda v: v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes"),
    "upper": lambda v: str(v).upper(),
    "lower": lambda v: str(v).lower(),
    "strip": lambda v: str(v).strip(),
    "null": lambda _: None,
}


def list_transforms() -> list:
    """Return available transform names."""
    return list(_TRANSFORMS.keys())


def apply_transform(value: Any, transform: str) -> Any:
    """Apply a named transform to a value."""
    if transform not in _TRANSFORMS:
        raise TransformError(
            f"Unknown transform '{transform}'. Available: {list_transforms()}"
        )
    try:
        return _TRANSFORMS[transform](value)
    except (ValueError, TypeError) as exc:
        raise TransformError(
            f"Transform '{transform}' failed on value {value!r}: {exc}"
        ) from exc


def apply_transforms_to_patch(patch: dict, transforms: Dict[str, str]) -> dict:
    """Apply per-key transforms to patch values.

    transforms is a dict mapping dot-notation key -> transform name.
    Returns a new patch dict with transformed values.
    """
    if not isinstance(patch, dict):
        raise TransformError("patch must be a dict")

    result = dict(patch)
    for key_path, transform in transforms.items():
        keys = key_path.split(".")
        _apply_at_path(result, keys, transform)
    return result


def _apply_at_path(data: dict, keys: list, transform: str) -> None:
    """Mutate data in-place, applying transform at the nested key path."""
    for k in keys[:-1]:
        if k not in data or not isinstance(data[k], dict):
            return
        data = data[k]
    leaf = keys[-1]
    if leaf in data:
        data[leaf] = apply_transform(data[leaf], transform)
