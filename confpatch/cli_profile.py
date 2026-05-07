"""CLI commands for managing named patch profiles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from confpatch.profile import (
    ProfileError,
    Profile,
    delete_profile,
    get_profile,
    load_profiles,
    save_profile,
)
from confpatch.patch import apply_patch
from confpatch.loaders import load_config, save_config


def cmd_profile_save(args: argparse.Namespace) -> int:
    try:
        patch_data = json.loads(Path(args.patch).read_text())
    except Exception as exc:
        print(f"error: could not read patch file: {exc}", file=sys.stderr)
        return 1
    profile = Profile(
        name=args.name,
        patch=patch_data,
        description=args.description or "",
        tags=args.tags or [],
    )
    store_dir = Path(args.store)
    try:
        save_profile(profile, store_dir)
        print(f"Profile '{args.name}' saved.")
        return 0
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def cmd_profile_apply(args: argparse.Namespace) -> int:
    store_dir = Path(args.store)
    config_path = Path(args.config)
    try:
        profile = get_profile(args.name, store_dir)
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        config = load_config(config_path)
        result = apply_patch(config, profile.patch)
        if not args.dry_run:
            save_config(result, config_path)
            print(f"Applied profile '{args.name}' to {config_path}")
        else:
            print(f"[dry-run] Would apply profile '{args.name}' to {config_path}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def cmd_profile_list(args: argparse.Namespace) -> int:
    store_dir = Path(args.store)
    profiles = load_profiles(store_dir)
    if not profiles:
        print("No profiles saved.")
        return 0
    for p in profiles:
        tags = ", ".join(p.tags) if p.tags else "-"
        print(f"  {p.name:20s}  tags=[{tags}]  {p.description}")
    return 0


def cmd_profile_delete(args: argparse.Namespace) -> int:
    store_dir = Path(args.store)
    try:
        delete_profile(args.name, store_dir)
        print(f"Profile '{args.name}' deleted.")
        return 0
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def register_profile_commands(subparsers: argparse._SubParsersAction, default_store: str) -> None:
    p = subparsers.add_parser("profile-save", help="Save a named patch profile")
    p.add_argument("name"); p.add_argument("patch")
    p.add_argument("--description", default=""); p.add_argument("--tags", nargs="*")
    p.add_argument("--store", default=default_store); p.set_defaults(func=cmd_profile_save)

    p = subparsers.add_parser("profile-apply", help="Apply a named patch profile")
    p.add_argument("name"); p.add_argument("config")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--store", default=default_store)
    p.set_defaults(func=cmd_profile_apply)

    p = subparsers.add_parser("profile-list", help="List saved profiles")
    p.add_argument("--store", default=default_store); p.set_defaults(func=cmd_profile_list)

    p = subparsers.add_parser("profile-delete", help="Delete a named profile")
    p.add_argument("name"); p.add_argument("--store", default=default_store)
    p.set_defaults(func=cmd_profile_delete)
