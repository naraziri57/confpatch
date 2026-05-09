"""CLI commands for tag-based patch grouping."""

from __future__ import annotations

from pathlib import Path

from confpatch.tag import (
    TagError,
    add_tag,
    remove_tag,
    get_patches_for_tag,
    list_tags,
)


def cmd_tag_add(args) -> int:
    config = Path(args.config)
    if not config.exists():
        print(f"Error: config file not found: {config}")
        return 1
    try:
        store = add_tag(config, args.tag, args.patch)
        print(f"Tagged '{args.patch}' with '{args.tag}'.")
        return 0
    except TagError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_tag_remove(args) -> int:
    config = Path(args.config)
    if not config.exists():
        print(f"Error: config file not found: {config}")
        return 1
    try:
        remove_tag(config, args.tag, getattr(args, "patch", None))
        print(f"Removed tag '{args.tag}'.")
        return 0
    except TagError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_tag_list(args) -> int:
    config = Path(args.config)
    if not config.exists():
        print(f"Error: config file not found: {config}")
        return 1
    tags = list_tags(config)
    if not tags:
        print("No tags defined.")
    else:
        for t in tags:
            print(f"  {t}")
    return 0


def cmd_tag_show(args) -> int:
    config = Path(args.config)
    if not config.exists():
        print(f"Error: config file not found: {config}")
        return 1
    try:
        patches = get_patches_for_tag(config, args.tag)
        if not patches:
            print(f"No patches under tag '{args.tag}'.")
        else:
            for p in patches:
                print(f"  {p}")
        return 0
    except TagError as exc:
        print(f"Error: {exc}")
        return 1


def register_tag_commands(subparsers):
    tag_parser = subparsers.add_parser("tag", help="Manage patch tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd")

    p_add = tag_sub.add_parser("add", help="Tag a patch")
    p_add.add_argument("config")
    p_add.add_argument("tag")
    p_add.add_argument("patch")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag")
    p_rm.add_argument("config")
    p_rm.add_argument("tag")
    p_rm.add_argument("--patch", default=None)
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List all tags")
    p_ls.add_argument("config")
    p_ls.set_defaults(func=cmd_tag_list)

    p_show = tag_sub.add_parser("show", help="Show patches for a tag")
    p_show.add_argument("config")
    p_show.add_argument("tag")
    p_show.set_defaults(func=cmd_tag_show)
