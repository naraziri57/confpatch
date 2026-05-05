"""confpatch — Minimal utility to apply structured patches to YAML/TOML config files."""

from confpatch.patch import apply_patch, load_patch

__version__ = "0.1.0"
__all__ = ["apply_patch", "load_patch"]
