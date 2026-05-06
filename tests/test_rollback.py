"""Tests for confpatch.rollback module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from confpatch.rollback import rollback, get_last_entry, RollbackError


@pytest.fixture()
def tmp_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("key: new_value\n")
    return cfg


@pytest.fixture()
def tmp_backup(tmp_path: Path) -> Path:
    bak = tmp_path / "config.yaml.bak"
    bak.write_text("key: original_value\n")
    return bak


def _make_entry(backup_path: str):
    entry = MagicMock()
    entry.backup_path = backup_path
    entry.timestamp = "2024-01-01T00:00:00"
    return entry


def test_get_last_entry_no_history(tmp_config):
    with patch("confpatch.rollback.load_history", return_value=[]):
        with pytest.raises(RollbackError, match="No history"):
            get_last_entry(tmp_config)


def test_get_last_entry_history_error(tmp_config):
    from confpatch.history import HistoryError
    with patch("confpatch.rollback.load_history", side_effect=HistoryError("oops")):
        with pytest.raises(RollbackError, match="Could not load history"):
            get_last_entry(tmp_config)


def test_get_last_entry_returns_last(tmp_config):
    entries = [_make_entry("/a"), _make_entry("/b")]
    with patch("confpatch.rollback.load_history", return_value=entries):
        result = get_last_entry(tmp_config)
    assert result.backup_path == "/b"


def test_rollback_no_backup_path(tmp_config):
    entry = _make_entry(None)
    with patch("confpatch.rollback.load_history", return_value=[entry]):
        with pytest.raises(RollbackError, match="no associated backup"):
            rollback(tmp_config)


def test_rollback_backup_missing(tmp_config, tmp_path):
    missing = str(tmp_path / "nonexistent.bak")
    entry = _make_entry(missing)
    with patch("confpatch.rollback.load_history", return_value=[entry]):
        with pytest.raises(RollbackError, match="Backup file not found"):
            rollback(tmp_config)


def test_rollback_success(tmp_config, tmp_backup):
    entry = _make_entry(str(tmp_backup))
    with patch("confpatch.rollback.load_history", return_value=[entry]):
        with patch("confpatch.rollback.restore_backup", return_value=tmp_config) as mock_restore:
            result = rollback(tmp_config)
    mock_restore.assert_called_once_with(tmp_backup, tmp_config)
    assert result == tmp_config


def test_rollback_restore_error(tmp_config, tmp_backup):
    from confpatch.backup import BackupError
    entry = _make_entry(str(tmp_backup))
    with patch("confpatch.rollback.load_history", return_value=[entry]):
        with patch("confpatch.rollback.restore_backup", side_effect=BackupError("fail")):
            with pytest.raises(RollbackError, match="Restore failed"):
                rollback(tmp_config)
