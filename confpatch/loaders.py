"""File format loaders and writers for YAML and TOML configs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict:
    """Load a YAML or TOML config file based on file extension."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        return _load_yaml(path)
    elif suffix == ".toml":
        return _load_toml(path)
    else:
        raise ValueError(f"Unsupported file format: '{suffix}'. Use .yaml, .yml, or .toml")


def save_config(data: dict, path: str | Path) -> None:
    """Save a config dict to a YAML or TOML file based on file extension."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        _save_yaml(data, path)
    elif suffix == ".toml":
        _save_toml(data, path)
    else:
        raise ValueError(f"Unsupported file format: '{suffix}'. Use .yaml, .yml, or .toml")


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for YAML support: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _save_yaml(data: dict, path: Path) -> None:
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for YAML support: pip install pyyaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _load_toml(path: Path) -> dict:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            raise ImportError("tomli is required for TOML support on Python <3.11: pip install tomli")
    with open(path, "rb") as f:
        return tomllib.load(f)


def _save_toml(data: dict, path: Path) -> None:
    try:
        import tomli_w
    except ImportError:
        raise ImportError("tomli-w is required for writing TOML files: pip install tomli-w")
    with open(path, "wb") as f:
        tomli_w.dump(data, f)
