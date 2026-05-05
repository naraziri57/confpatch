"""Tests for confpatch.backup module."""

import os
import pytest
from pathlib import Path
from confpatch.backup import (
    create_backup,
    restore_backup,
    list_backups,
    delete_backup,
    BackupError,
)


@pytest.fixture
def sample_config(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("key: value\n")
    return str(config)


def test_create_backup_returns_path(sample_config, tmp_path):
    backup_path = create_backup(sample_config, backup_dir=str(tmp_path))
    assert os.path.exists(backup_path)
    assert backup_path.endswith(".bak.yaml")


def test_create_backup_preserves_content(sample_config, tmp_path):
    backup_path = create_backup(sample_config, backup_dir=str(tmp_path))
    original = Path(sample_config).read_text()
    backup = Path(backup_path).read_text()
    assert original == backup


def test_create_backup_default_dir(sample_config):
    backup_path = create_backup(sample_config)
    assert os.path.exists(backup_path)
    assert Path(backup_path).parent == Path(sample_config).parent
    os.remove(backup_path)


def test_create_backup_file_not_found(tmp_path):
    with pytest.raises(BackupError, match="File not found"):
        create_backup(str(tmp_path / "nonexistent.yaml"))


def test_restore_backup(sample_config, tmp_path):
    backup_path = create_backup(sample_config, backup_dir=str(tmp_path))
    Path(sample_config).write_text("key: changed\n")
    restore_backup(backup_path, sample_config)
    assert Path(sample_config).read_text() == "key: value\n"


def test_restore_backup_not_found(sample_config, tmp_path):
    with pytest.raises(BackupError, match="Backup file not found"):
        restore_backup(str(tmp_path / "ghost.bak.yaml"), sample_config)


def test_list_backups_empty(sample_config, tmp_path):
    result = list_backups(sample_config, backup_dir=str(tmp_path))
    assert result == []


def test_list_backups_finds_backups(sample_config, tmp_path):
    create_backup(sample_config, backup_dir=str(tmp_path))
    create_backup(sample_config, backup_dir=str(tmp_path))
    result = list_backups(sample_config, backup_dir=str(tmp_path))
    assert len(result) == 2


def test_delete_backup(sample_config, tmp_path):
    backup_path = create_backup(sample_config, backup_dir=str(tmp_path))
    delete_backup(backup_path)
    assert not os.path.exists(backup_path)


def test_delete_backup_not_found(tmp_path):
    with pytest.raises(BackupError, match="Backup file not found"):
        delete_backup(str(tmp_path / "ghost.bak.yaml"))
