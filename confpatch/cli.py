"""CLI entry point for confpatch."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.patch import load_patch, apply_patch
from confpatch.validator import validate_patch_structure, validate_keys, PatchValidationError
from confpatch.diff import compute_diff, format_diff
from confpatch.cli_backup import register_backup_commands
from confpatch.cli_rollback import register_rollback_commands


def _detect_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return "yaml"
    if suffix == ".toml":
        return "toml"
    raise ValueError(f"Cannot detect format from extension: {suffix}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="confpatch",
        description="Apply structured patches to YAML/TOML config files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # apply subcommand
    apply_parser = subparsers.add_parser("apply", help="Apply a patch to a config file")
    apply_parser.add_argument("config", help="Path to the config file")
    apply_parser.add_argument("patch", help="Path to the patch file (JSON/YAML)")
    apply_parser.add_argument("--format", choices=["yaml", "toml"], default=None)
    apply_parser.add_argument("--dry-run", action="store_true", default=False)
    apply_parser.add_argument("--no-backup", action="store_true", default=False)
    apply_parser.set_defaults(func=cmd_apply)

    register_backup_commands(subparsers)
    register_rollback_commands(subparsers)

    return parser


def cmd_apply(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    patch_path = Path(args.patch)

    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    if not patch_path.exists():
        print(f"Error: patch file not found: {patch_path}")
        return 1

    fmt = args.format or _detect_format(config_path)

    try:
        config = load_config(config_path, fmt)
        patch = load_patch(patch_path)
        validate_patch_structure(patch)
        validate_keys(patch)
    except (PatchValidationError, ValueError) as exc:
        print(f"Validation error: {exc}")
        return 1

    patched = apply_patch(config, patch)
    diff = compute_diff(config, patched)

    if args.dry_run:
        print(format_diff(diff))
        return 0

    if not args.no_backup:
        from confpatch.backup import create_backup
        create_backup(config_path)

    save_config(config_path, patched, fmt)
    print(format_diff(diff))
    print(f"Patch applied to {config_path}.")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
