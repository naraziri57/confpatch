"""Minimal CLI for confpatch.

Usage:
    confpatch apply <config_file> <patch_file> [--output <out_file>] [--format yaml|toml]
"""

import argparse
import sys
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.patch import apply_patch, load_patch
from confpatch.validator import (
    PatchValidationError,
    validate_format,
    validate_keys,
    validate_patch_structure,
)


def _detect_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in ("yml", "yaml"):
        return "yaml"
    if suffix == "toml":
        return "toml"
    return "yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="confpatch",
        description="Apply structured patches to YAML/TOML config files.",
    )
    sub = parser.add_subparsers(dest="command")

    apply_cmd = sub.add_parser("apply", help="Apply a patch file to a config file")
    apply_cmd.add_argument("config", help="Path to the config file")
    apply_cmd.add_argument("patch", help="Path to the patch file")
    apply_cmd.add_argument(
        "--output", "-o", default=None,
        help="Output path (defaults to overwriting the config file)",
    )
    apply_cmd.add_argument(
        "--format", "-f", default=None, choices=("yaml", "toml"),
        help="Force a specific format (auto-detected from extension by default)",
    )
    return parser


def cmd_apply(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    patch_path = Path(args.patch)

    fmt = args.format or _detect_format(config_path)

    try:
        validate_format(fmt)
        config = load_config(config_path, fmt=fmt)
        patch = load_patch(patch_path)
        validate_patch_structure(patch)
        validate_keys(patch)
        updated = apply_patch(config, patch)
    except (PatchValidationError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.output) if args.output else config_path
    save_config(updated, out_path, fmt=fmt)
    print(f"Patched {config_path} -> {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "apply":
        return cmd_apply(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
