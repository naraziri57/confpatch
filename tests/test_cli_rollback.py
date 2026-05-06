"""Tests for confpatch.cli_rollback module."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from confpatch.cli_rollback import cmd_rollback, register_rollback_commands
from confpatch.rollback import RollbackError


def make_args(config: str, dry_run: bool = False) -> argparse.Namespace:
    return argparse.Namespace(config=config, dry_run=dry_run)


def test_cmd_rollback_config_not_found(tmp_path, capsys):
    args = make_args(str(tmp_path / "missing.yaml"))
    rc = cmd_rollback(args)
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_cmd_rollback_success(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("x: 1\n")
    args = make_args(str(cfg))
    with patch("confpatch.cli_rollback.rollback", return_value=cfg):
        rc = cmd_rollback(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "Rolled back" in captured.out


def test_cmd_rollback_failure(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("x: 1\n")
    args = make_args(str(cfg))
    with patch("confpatch.cli_rollback.rollback", side_effect=RollbackError("no backup")):
        rc = cmd_rollback(args)
    assert rc == 1
    captured = capsys.readouterr()
    assert "Rollback failed" in captured.out


def test_cmd_rollback_dry_run(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("x: 1\n")
    entry = MagicMock()
    entry.backup_path = "/some/backup"
    entry.timestamp = "2024-01-01T00:00:00"
    args = make_args(str(cfg), dry_run=True)
    with patch("confpatch.cli_rollback.get_last_entry", return_value=entry):
        rc = cmd_rollback(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "Would restore" in captured.out


def test_cmd_rollback_dry_run_error(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("x: 1\n")
    args = make_args(str(cfg), dry_run=True)
    with patch("confpatch.cli_rollback.get_last_entry", side_effect=RollbackError("nothing")):
        rc = cmd_rollback(args)
    assert rc == 1


def test_register_rollback_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_rollback_commands(subparsers)
    args = parser.parse_args(["rollback", "myconfig.yaml"])
    assert args.config == "myconfig.yaml"
    assert args.dry_run is False
    assert args.func is cmd_rollback
