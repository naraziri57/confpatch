"""Tests for confpatch.snapshot."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from confpatch.snapshot import (
    Snapshot,
    SnapshotError,
    get_latest_snapshot,
    load_snapshots,
    save_snapshot,
)


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("key: value\n", encoding="utf-8")
    return cfg


def test_save_snapshot_returns_snapshot(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    snap = save_snapshot(tmp_config, {"key": "value"}, snapshot_dir=snap_dir)
    assert isinstance(snap, Snapshot)
    assert snap.data == {"key": "value"}
    assert snap.config_path == str(tmp_config)


def test_save_snapshot_persists(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    save_snapshot(tmp_config, {"a": 1}, snapshot_dir=snap_dir)
    snaps = load_snapshots(tmp_config, snapshot_dir=snap_dir)
    assert len(snaps) == 1
    assert snaps[0].data == {"a": 1}


def test_save_multiple_snapshots(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    save_snapshot(tmp_config, {"v": 1}, snapshot_dir=snap_dir)
    save_snapshot(tmp_config, {"v": 2}, snapshot_dir=snap_dir)
    snaps = load_snapshots(tmp_config, snapshot_dir=snap_dir)
    assert len(snaps) == 2
    assert snaps[0].data["v"] == 1
    assert snaps[1].data["v"] == 2


def test_load_snapshots_empty(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    snaps = load_snapshots(tmp_config, snapshot_dir=snap_dir)
    assert snaps == []


def test_get_latest_snapshot_none(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    result = get_latest_snapshot(tmp_config, snapshot_dir=snap_dir)
    assert result is None


def test_get_latest_snapshot_returns_last(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    save_snapshot(tmp_config, {"v": 1}, snapshot_dir=snap_dir)
    save_snapshot(tmp_config, {"v": 99}, snapshot_dir=snap_dir)
    latest = get_latest_snapshot(tmp_config, snapshot_dir=snap_dir)
    assert latest is not None
    assert latest.data["v"] == 99


def test_save_snapshot_file_not_found(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(SnapshotError, match="not found"):
        save_snapshot(missing, {"x": 1})


def test_load_snapshots_corrupt_file(tmp_config, tmp_path):
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    snap_file = snap_dir / "config_yaml.snapshots.json"
    snap_file.write_text("NOT JSON", encoding="utf-8")
    with pytest.raises(SnapshotError, match="Failed to load"):
        load_snapshots(tmp_config, snapshot_dir=snap_dir)


def test_snapshot_roundtrip():
    snap = Snapshot(config_path="/tmp/cfg.yaml", data={"x": 42}, timestamp=1234567890.0)
    d = snap.to_dict()
    restored = Snapshot.from_dict(d)
    assert restored.config_path == snap.config_path
    assert restored.data == snap.data
    assert restored.timestamp == snap.timestamp
