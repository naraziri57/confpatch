"""Tests for confpatch.cli_snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from confpatch.cli_snapshot import cmd_snapshot, cmd_list_snapshots, cmd_show_latest
from confpatch.snapshot import Snapshot


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"config": "config.yaml"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_snapshot_file_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"))
    result = cmd_snapshot(args)
    assert result == 1


def test_cmd_snapshot_success(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("key: value\n", encoding="utf-8")
    args = make_args(config=str(cfg))

    with patch("confpatch.cli_snapshot.load_config", return_value={"key": "value"}), \
         patch("confpatch.cli_snapshot.save_snapshot") as mock_save:
        mock_snap = MagicMock()
        mock_snap.timestamp = 1700000000.0
        mock_save.return_value = mock_snap
        result = cmd_snapshot(args)

    assert result == 0


def test_cmd_snapshot_error(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("key: value\n", encoding="utf-8")
    args = make_args(config=str(cfg))

    from confpatch.snapshot import SnapshotError
    with patch("confpatch.cli_snapshot.load_config", return_value={}), \
         patch("confpatch.cli_snapshot.save_snapshot", side_effect=SnapshotError("boom")):
        result = cmd_snapshot(args)
    assert result == 1


def test_cmd_list_snapshots_empty(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("", encoding="utf-8")
    args = make_args(config=str(cfg))

    with patch("confpatch.cli_snapshot.load_snapshots", return_value=[]):
        result = cmd_list_snapshots(args)
    assert result == 0


def test_cmd_list_snapshots_with_entries(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    args = make_args(config=str(cfg))
    snaps = [
        Snapshot(config_path=str(cfg), data={"a": 1}, timestamp=1000.0),
        Snapshot(config_path=str(cfg), data={"a": 2}, timestamp=2000.0),
    ]
    with patch("confpatch.cli_snapshot.load_snapshots", return_value=snaps):
        result = cmd_list_snapshots(args)
    assert result == 0
    out = capsys.readouterr().out
    assert "[0]" in out
    assert "[1]" in out


def test_cmd_show_latest_none(tmp_path):
    cfg = tmp_path / "config.yaml"
    args = make_args(config=str(cfg))
    with patch("confpatch.cli_snapshot.get_latest_snapshot", return_value=None):
        result = cmd_show_latest(args)
    assert result == 1


def test_cmd_show_latest_success(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    args = make_args(config=str(cfg))
    snap = Snapshot(config_path=str(cfg), data={"x": 7}, timestamp=999.0)
    with patch("confpatch.cli_snapshot.get_latest_snapshot", return_value=snap):
        result = cmd_show_latest(args)
    assert result == 0
    out = capsys.readouterr().out
    assert "\"x\"" in out or "x" in out
