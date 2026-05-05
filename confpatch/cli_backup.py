"""CLI subcommands for backup and restore operations."""

import argparse
from confpatch.backup import (
    create_backup,
    restore_backup,
    list_backups,
    delete_backup,
    BackupError,
)


def cmd_backup(args: argparse.Namespace) -> int:
    """Create a backup of a config file."""
    try:
        path = create_backup(args.file, backup_dir=args.backup_dir)
        print(f"Backup created: {path}")
        return 0
    except BackupError as e:
        print(f"Error: {e}")
        return 1


def cmd_restore(args: argparse.Namespace) -> int:
    """Restore a config file from a backup."""
    try:
        restore_backup(args.backup, args.file)
        print(f"Restored {args.file} from {args.backup}")
        return 0
    except BackupError as e:
        print(f"Error: {e}")
        return 1


def cmd_list_backups(args: argparse.Namespace) -> int:
    """List available backups for a config file."""
    backups = list_backups(args.file, backup_dir=args.backup_dir)
    if not backups:
        print(f"No backups found for {args.file}")
    else:
        print(f"Backups for {args.file}:")
        for b in backups:
            print(f"  {b}")
    return 0


def cmd_delete_backup(args: argparse.Namespace) -> int:
    """Delete a specific backup file."""
    try:
        delete_backup(args.backup)
        print(f"Deleted backup: {args.backup}")
        return 0
    except BackupError as e:
        print(f"Error: {e}")
        return 1


def register_backup_commands(subparsers) -> None:
    """Register backup-related subcommands onto an existing subparsers object."""
    p_backup = subparsers.add_parser("backup", help="Create a backup of a config file")
    p_backup.add_argument("file", help="Path to the config file")
    p_backup.add_argument("--backup-dir", default=None, help="Directory to store backups")
    p_backup.set_defaults(func=cmd_backup)

    p_restore = subparsers.add_parser("restore", help="Restore a config file from a backup")
    p_restore.add_argument("file", help="Target config file path")
    p_restore.add_argument("backup", help="Path to the backup file")
    p_restore.set_defaults(func=cmd_restore)

    p_list = subparsers.add_parser("list-backups", help="List backups for a config file")
    p_list.add_argument("file", help="Path to the config file")
    p_list.add_argument("--backup-dir", default=None, help="Directory to search for backups")
    p_list.set_defaults(func=cmd_list_backups)

    p_del = subparsers.add_parser("delete-backup", help="Delete a specific backup file")
    p_del.add_argument("backup", help="Path to the backup file to delete")
    p_del.set_defaults(func=cmd_delete_backup)
