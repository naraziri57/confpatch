"""Tests for confpatch.history module."""

import json
from pathlib import Path

import pytest

from confpatch.history import (
    HistoryEntry,
    HistoryError,
    append_history,
    clear_history,
    load_history,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def make_entry(**kwargs):
    defaults = dict(
        config_file="config.yaml",
        patch_file="patch.yaml",
        changes=[{"key": "foo", "old": 1, "new": 2}],
    )
    defaults.update(kwargs)
    return HistoryEntry.create(**defaults)


def test_load_history_empty(tmp_dir):
    entries = load_history(tmp_dir)
    assert entries == []


def test_append_and_load_history(tmp_dir):
    entry = make_entry()
    append_history(entry, directory=tmp_dir)
    loaded = load_history(tmp_dir)
    assert len(loaded) == 1
    assert loaded[0].config_file == "config.yaml"
    assert loaded[0].patch_file == "patch.yaml"


def test_append_multiple_entries(tmp_dir):
    for i in range(3):
        append_history(make_entry(config_file=f"config{i}.yaml"), directory=tmp_dir)
    loaded = load_history(tmp_dir)
    assert len(loaded) == 3
    assert loaded[2].config_file == "config2.yaml"


def test_history_entry_has_timestamp(tmp_dir):
    entry = make_entry()
    append_history(entry, directory=tmp_dir)
    loaded = load_history(tmp_dir)
    assert loaded[0].timestamp is not None
    assert "T" in loaded[0].timestamp  # ISO format


def test_history_entry_with_backup_path(tmp_dir):
    entry = make_entry(backup_path="/tmp/backup.yaml")
    append_history(entry, directory=tmp_dir)
    loaded = load_history(tmp_dir)
    assert loaded[0].backup_path == "/tmp/backup.yaml"


def test_history_entry_with_tags(tmp_dir):
    entry = make_entry(tags=["production", "hotfix"])
    append_history(entry, directory=tmp_dir)
    loaded = load_history(tmp_dir)
    assert loaded[0].tags == ["production", "hotfix"]


def test_clear_history(tmp_dir):
    append_history(make_entry(), directory=tmp_dir)
    clear_history(tmp_dir)
    assert load_history(tmp_dir) == []


def test_clear_history_no_file(tmp_dir):
    # Should not raise even if file doesn't exist
    clear_history(tmp_dir)


def test_load_history_corrupt_file(tmp_dir):
    history_file = tmp_dir / ".confpatch_history.json"
    history_file.write_text("not valid json", encoding="utf-8")
    with pytest.raises(HistoryError):
        load_history(tmp_dir)


def test_append_history_returns_path(tmp_dir):
    path = append_history(make_entry(), directory=tmp_dir)
    assert isinstance(path, Path)
    assert path.exists()
