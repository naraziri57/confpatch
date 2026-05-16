"""CLI commands for preset management."""

from __future__ import annotations

from pathlib import Path

from confpatch.loaders import load_config
from confpatch.patch import apply_patch, load_patch
from confpatch.preset import PresetError, Preset, delete_preset, get_preset, load_presets, save_preset


def cmd_preset_save(args) -> None:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return
    patch_path = Path(args.patch)
    if not patch_path.exists():
        print(f"Error: patch file not found: {patch_path}")
        return
    try:
        patch = load_patch(str(patch_path))
        preset = Preset(
            name=args.name,
            patch=patch,
            description=getattr(args, "description", ""),
            tags=getattr(args, "tags", []) or [],
        )
        save_preset(config_path, preset)
        print(f"Preset '{args.name}' saved.")
    except PresetError as e:
        print(f"Error: {e}")


def cmd_preset_apply(args) -> None:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return
    try:
        preset = get_preset(config_path, args.name)
        config = load_config(str(config_path))
        updated = apply_patch(config, preset.patch)
        from confpatch.loaders import save_config
        fmt = config_path.suffix.lstrip(".")
        save_config(updated, str(config_path), fmt=fmt)
        print(f"Preset '{args.name}' applied to {config_path}.")
    except PresetError as e:
        print(f"Error: {e}")


def cmd_preset_list(args) -> None:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return
    try:
        presets = load_presets(config_path)
        if not presets:
            print("No presets saved.")
            return
        for name, preset in presets.items():
            desc = f" — {preset.description}" if preset.description else ""
            tags = f" [{', '.join(preset.tags)}]" if preset.tags else ""
            print(f"  {name}{desc}{tags}")
    except PresetError as e:
        print(f"Error: {e}")


def cmd_preset_delete(args) -> None:
    config_path = Path(args.config)
    try:
        delete_preset(config_path, args.name)
        print(f"Preset '{args.name}' deleted.")
    except PresetError as e:
        print(f"Error: {e}")


def register_preset_commands(subparsers) -> None:
    p = subparsers.add_parser("preset-save", help="Save a patch as a named preset")
    p.add_argument("config"); p.add_argument("patch"); p.add_argument("name")
    p.add_argument("--description", default=""); p.add_argument("--tags", nargs="*")
    p.set_defaults(func=cmd_preset_save)

    p = subparsers.add_parser("preset-apply", help="Apply a saved preset")
    p.add_argument("config"); p.add_argument("name")
    p.set_defaults(func=cmd_preset_apply)

    p = subparsers.add_parser("preset-list", help="List saved presets")
    p.add_argument("config")
    p.set_defaults(func=cmd_preset_list)

    p = subparsers.add_parser("preset-delete", help="Delete a saved preset")
    p.add_argument("config"); p.add_argument("name")
    p.set_defaults(func=cmd_preset_delete)
