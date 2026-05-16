"""Tests for confpatch.metrics."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from confpatch.metrics import (
    MetricEntry,
    MetricsError,
    load_metrics,
    record_metric,
    summarize_metrics,
    _metrics_path,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "app.yaml"
    f.write_text("key: value\n")
    return str(f)


def _make_entry(config_file, patch_file="patch.yaml", keys=2, ms=10.0, success=True):
    return MetricEntry(
        config_file=config_file,
        patch_file=patch_file,
        keys_changed=keys,
        duration_ms=ms,
        success=success,
        timestamp=time.time(),
    )


def test_load_metrics_empty(config_file):
    assert load_metrics(config_file) == []


def test_record_metric_creates_file(config_file):
    entry = _make_entry(config_file)
    record_metric(entry)
    path = _metrics_path(config_file)
    assert path.exists()


def test_record_metric_returns_entry(config_file):
    entry = _make_entry(config_file)
    result = record_metric(entry)
    assert result.config_file == config_file
    assert result.keys_changed == 2


def test_load_metrics_after_record(config_file):
    entry = _make_entry(config_file, keys=5)
    record_metric(entry)
    loaded = load_metrics(config_file)
    assert len(loaded) == 1
    assert loaded[0].keys_changed == 5


def test_record_multiple_entries(config_file):
    for i in range(3):
        record_metric(_make_entry(config_file, keys=i))
    loaded = load_metrics(config_file)
    assert len(loaded) == 3


def test_metric_entry_to_dict_roundtrip(config_file):
    entry = _make_entry(config_file, keys=7, ms=42.5, success=False)
    d = entry.to_dict()
    restored = MetricEntry.from_dict(d)
    assert restored.keys_changed == 7
    assert restored.success is False
    assert restored.duration_ms == 42.5


def test_summarize_metrics_empty(config_file):
    summary = summarize_metrics(config_file)
    assert summary["total"] == 0
    assert summary["avg_duration_ms"] == 0.0


def test_summarize_metrics_counts(config_file):
    record_metric(_make_entry(config_file, keys=3, ms=10.0, success=True))
    record_metric(_make_entry(config_file, keys=1, ms=20.0, success=False))
    summary = summarize_metrics(config_file)
    assert summary["total"] == 2
    assert summary["successful"] == 1
    assert summary["failed"] == 1
    assert summary["total_keys_changed"] == 4
    assert summary["avg_duration_ms"] == 15.0


def test_load_metrics_corrupt_file(config_file):
    path = _metrics_path(config_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not valid json")
    with pytest.raises(MetricsError):
        load_metrics(config_file)
