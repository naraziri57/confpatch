"""CLI commands for alias management."""

from __future__ import annotations

from pathlib import Path

from confpatch.alias import (
    AliasError,
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
)


def cmd_alias_add(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    try:
        add_alias(config_path, args.name, args.patch)
        print(f"Alias '{args.name}' -> '{args.patch}' saved.")
        return 0
    except AliasError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_alias_remove(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    try:
        remove_alias(config_path, args.name)
        print(f"Alias '{args.name}' removed.")
        return 0
    except AliasError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_alias_list(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    entries = list_aliases(config_path)
    if not entries:
        print("No aliases defined.")
    else:
        for name, patch in entries:
            print(f"  {name:20s} -> {patch}")
    return 0


def cmd_alias_resolve(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    try:
        resolved = resolve_alias(config_path, args.name)
        print(resolved)
        return 0
    except AliasError as exc:
        print(f"Error: {exc}")
        return 1


def register_alias_commands(subparsers):
    p_add = subparsers.add_parser("alias-add", help="Add a patch alias")
    p_add.add_argument("config", help="Config file")
    p_add.add_argument("name", help="Alias name")
    p_add.add_argument("patch", help="Path to patch file")
    p_add.set_defaults(func=cmd_alias_add)

    p_rm = subparsers.add_parser("alias-remove", help="Remove a patch alias")
    p_rm.add_argument("config", help="Config file")
    p_rm.add_argument("name", help="Alias name")
    p_rm.set_defaults(func=cmd_alias_remove)

    p_ls = subparsers.add_parser("alias-list", help="List all aliases")
    p_ls.add_argument("config", help="Config file")
    p_ls.set_defaults(func=cmd_alias_list)

    p_res = subparsers.add_parser("alias-resolve", help="Resolve an alias to its path")
    p_res.add_argument("config", help="Config file")
    p_res.add_argument("name", help="Alias name")
    p_res.set_defaults(func=cmd_alias_resolve)
