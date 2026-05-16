"""CLI commands for the config key index feature."""

from __future__ import annotations

import argparse

from confpatch.index import IndexError, build_index, load_index, save_index, search_index


def cmd_build_index(args: argparse.Namespace) -> None:
    files = args.files
    out = args.output
    try:
        entries = build_index(files)
    except IndexError as e:
        print(f"[error] {e}")
        return
    save_index(entries, out)
    print(f"[ok] indexed {len(entries)} keys from {len(files)} file(s) -> {out}")


def cmd_search_index(args: argparse.Namespace) -> None:
    index_file = args.index
    query = args.query
    entries = load_index(index_file)
    if not entries:
        print("[info] index is empty or not found")
        return
    results = search_index(entries, query)
    if not results:
        print(f"[info] no keys matching '{query}'")
        return
    for e in results:
        print(f"  {e.file}  {e.key} = {e.value!r}")


def cmd_list_index(args: argparse.Namespace) -> None:
    index_file = args.index
    entries = load_index(index_file)
    if not entries:
        print("[info] index is empty or not found")
        return
    for e in entries:
        print(f"  {e.file}  {e.key} = {e.value!r}")


def register_index_commands(subparsers: argparse._SubParsersAction) -> None:
    p_build = subparsers.add_parser("index-build", help="Build key index from config files")
    p_build.add_argument("files", nargs="+", help="Config files to index")
    p_build.add_argument("--output", default=".confpatch_index.json", help="Output index file")
    p_build.set_defaults(func=cmd_build_index)

    p_search = subparsers.add_parser("index-search", help="Search keys in the index")
    p_search.add_argument("query", help="Key substring to search for")
    p_search.add_argument("--index", default=".confpatch_index.json", help="Index file")
    p_search.set_defaults(func=cmd_search_index)

    p_list = subparsers.add_parser("index-list", help="List all indexed keys")
    p_list.add_argument("--index", default=".confpatch_index.json", help="Index file")
    p_list.set_defaults(func=cmd_list_index)
