"""CLI commands for annotation management."""
from __future__ import annotations

from pathlib import Path

from confpatch.annotate import AnnotateError, add_annotation, get_annotation, load_annotations, remove_annotation


def cmd_annotate_add(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    try:
        tags = args.tags.split(",") if getattr(args, "tags", None) else []
        ann = add_annotation(config_path, args.key, args.note, author=getattr(args, "author", "unknown"), tags=tags)
        print(f"Annotation added for key '{ann.key}' by {ann.author}.")
        return 0
    except AnnotateError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_annotate_remove(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    try:
        remove_annotation(config_path, args.key)
        print(f"Annotation removed for key '{args.key}'.")
        return 0
    except AnnotateError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_annotate_show(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    try:
        ann = get_annotation(config_path, args.key)
        print(f"Key:    {ann.key}")
        print(f"Note:   {ann.note}")
        print(f"Author: {ann.author}")
        if ann.tags:
            print(f"Tags:   {', '.join(ann.tags)}")
        return 0
    except AnnotateError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_annotate_list(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    annotations = load_annotations(config_path)
    if not annotations:
        print("No annotations found.")
        return 0
    for key, ann in annotations.items():
        tag_str = f" [{', '.join(ann.tags)}]" if ann.tags else ""
        print(f"  {key}: {ann.note} (by {ann.author}){tag_str}")
    return 0


def register_annotate_commands(subparsers) -> None:
    p = subparsers.add_parser("annotate-add", help="Add annotation to a config key")
    p.add_argument("config")
    p.add_argument("key")
    p.add_argument("note")
    p.add_argument("--author", default="unknown")
    p.add_argument("--tags", default="")
    p.set_defaults(func=cmd_annotate_add)

    p = subparsers.add_parser("annotate-remove", help="Remove annotation from a config key")
    p.add_argument("config")
    p.add_argument("key")
    p.set_defaults(func=cmd_annotate_remove)

    p = subparsers.add_parser("annotate-show", help="Show annotation for a config key")
    p.add_argument("config")
    p.add_argument("key")
    p.set_defaults(func=cmd_annotate_show)

    p = subparsers.add_parser("annotate-list", help="List all annotations for a config file")
    p.add_argument("config")
    p.set_defaults(func=cmd_annotate_list)
