"""CLI commands for snapshot management."""

from __future__ import annotations

import argparse
from pathlib import Path

from confpatch.loaders import load_config
from confpatch.snapshot import SnapshotError, get_latest_snapshot, load_snapshots, save_snapshot


def cmd_snapshot(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1

    try:
        data = load_config(config_path)
        snap = save_snapshot(config_path, data)
        print(f"Snapshot saved for {config_path} at {snap.timestamp:.0f}")
        return 0
    except SnapshotError as exc:
        print(f"Snapshot error: {exc}")
        return 1


def cmd_list_snapshots(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    try:
        snaps = load_snapshots(config_path)
        if not snaps:
            print(f"No snapshots found for {config_path}")
            return 0
        for i, snap in enumerate(snaps):
            print(f"  [{i}] timestamp={snap.timestamp:.0f}  keys={list(snap.data.keys())}")
        return 0
    except SnapshotError as exc:
        print(f"Error loading snapshots: {exc}")
        return 1


def cmd_show_latest(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    try:
        snap = get_latest_snapshot(config_path)
        if snap is None:
            print(f"No snapshots for {config_path}")
            return 1
        import json
        print(json.dumps(snap.data, indent=2))
        return 0
    except SnapshotError as exc:
        print(f"Error: {exc}")
        return 1


def register_snapshot_commands(subparsers: argparse._SubParsersAction) -> None:
    p_snap = subparsers.add_parser("snapshot", help="Save a snapshot of a config file")
    p_snap.add_argument("config", help="Path to the config file")
    p_snap.set_defaults(func=cmd_snapshot)

    p_list = subparsers.add_parser("snapshots", help="List snapshots for a config file")
    p_list.add_argument("config", help="Path to the config file")
    p_list.set_defaults(func=cmd_list_snapshots)

    p_latest = subparsers.add_parser("snapshot-show", help="Show the latest snapshot data")
    p_latest.add_argument("config", help="Path to the config file")
    p_latest.set_defaults(func=cmd_show_latest)
