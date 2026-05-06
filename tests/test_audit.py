"""Tests for confpatch.audit module."""

import pytest
from pathlib import Path

from confpatch.audit import AuditEntry, AuditError, record, load_audit


@pytest.fixture
def audit_file(tmp_path):
    return tmp_path / "audit.jsonl"


def test_record_creates_file(audit_file):
    record("config.yaml", ["key"], audit_path=audit_file)
    assert audit_file.exists()


def test_record_returns_entry(audit_file):
    entry = record("config.yaml", ["a.b"], dry_run=True, audit_path=audit_file)
    assert isinstance(entry, AuditEntry)
    assert entry.config_file == "config.yaml"
    assert entry.patch_keys == ["a.b"]
    assert entry.dry_run is True
    assert entry.success is True


def test_record_failure_entry(audit_file):
    entry = record(
        "config.toml",
        ["x"],
        success=False,
        error="something went wrong",
        audit_path=audit_file,
    )
    assert entry.success is False
    assert entry.error == "something went wrong"


def test_load_audit_empty(audit_file):
    entries = load_audit(audit_path=audit_file)
    assert entries == []


def test_load_audit_missing_file(tmp_path):
    entries = load_audit(audit_path=tmp_path / "nonexistent.jsonl")
    assert entries == []


def test_load_audit_round_trip(audit_file):
    record("a.yaml", ["foo"], audit_path=audit_file)
    record("b.yaml", ["bar", "baz"], dry_run=True, audit_path=audit_file)
    entries = load_audit(audit_path=audit_file)
    assert len(entries) == 2
    assert entries[0].config_file == "a.yaml"
    assert entries[1].patch_keys == ["bar", "baz"]
    assert entries[1].dry_run is True


def test_load_audit_preserves_timestamp(audit_file):
    entry = record("cfg.yaml", ["k"], audit_path=audit_file)
    loaded = load_audit(audit_path=audit_file)
    assert loaded[0].timestamp == entry.timestamp


def test_record_error_on_bad_path():
    bad_path = Path("/no_permission_root_dir/audit.jsonl")
    with pytest.raises(AuditError):
        record("cfg.yaml", ["k"], audit_path=bad_path)


def test_audit_entry_to_dict():
    entry = AuditEntry(config_file="x.yaml", patch_keys=["a"])
    d = entry.to_dict()
    assert d["config_file"] == "x.yaml"
    assert d["patch_keys"] == ["a"]
    assert "timestamp" in d
    assert "user" in d


def test_audit_entry_from_dict_roundtrip():
    entry = AuditEntry(config_file="z.toml", patch_keys=["p", "q"], dry_run=True)
    restored = AuditEntry.from_dict(entry.to_dict())
    assert restored.config_file == entry.config_file
    assert restored.patch_keys == entry.patch_keys
    assert restored.dry_run == entry.dry_run
