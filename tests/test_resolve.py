"""Tests for confpatch.resolve."""

from __future__ import annotations

import pytest

from confpatch.resolve import ResolveError, ResolveResult, resolve_refs


@pytest.fixture()
def tmp_ref_file(tmp_path):
    ref = tmp_path / "secret.txt"
    ref.write_text("supersecret\n")
    return tmp_path


def test_resolve_no_refs_returns_copy():
    config = {"host": "localhost", "port": 5432}
    result = resolve_refs(config)
    assert result.resolved == config
    assert not result.has_changes()


def test_resolve_file_ref(tmp_ref_file):
    config = {"password": "file://secret.txt", "host": "db"}
    result = resolve_refs(config, base_dir=tmp_ref_file)
    assert result.resolved["password"] == "supersecret"
    assert result.resolved["host"] == "db"
    assert result.has_changes()
    assert result.count() == 1


def test_resolve_nested_file_ref(tmp_ref_file):
    config = {"db": {"password": "file://secret.txt"}}
    result = resolve_refs(config, base_dir=tmp_ref_file)
    assert result.resolved["db"]["password"] == "supersecret"
    assert result.changes[0][0] == "db.password"


def test_resolve_missing_file_raises(tmp_path):
    config = {"token": "file://missing.txt"}
    with pytest.raises(ResolveError, match="not found"):
        resolve_refs(config, base_dir=tmp_path)


def test_resolve_non_dict_raises():
    with pytest.raises(ResolveError, match="must be a dict"):
        resolve_refs(["a", "b"])


def test_resolve_does_not_mutate_original(tmp_ref_file):
    config = {"key": "file://secret.txt"}
    original = dict(config)
    resolve_refs(config, base_dir=tmp_ref_file)
    assert config == original


def test_resolve_summary_no_changes():
    result = ResolveResult(resolved={}, changes=[])
    assert "No references" in result.summary()


def test_resolve_summary_with_changes():
    result = ResolveResult(resolved={}, changes=[("db.password", "file://secret.txt")])
    s = result.summary()
    assert "1" in s
    assert "db.password" in s


def test_resolve_list_values_passthrough(tmp_ref_file):
    config = {"items": ["a", "b", "c"]}
    result = resolve_refs(config, base_dir=tmp_ref_file)
    assert result.resolved["items"] == ["a", "b", "c"]
    assert not result.has_changes()


def test_resolve_multiple_refs(tmp_path):
    (tmp_path / "a.txt").write_text("alpha")
    (tmp_path / "b.txt").write_text("beta")
    config = {"x": "file://a.txt", "y": "file://b.txt"}
    result = resolve_refs(config, base_dir=tmp_path)
    assert result.resolved["x"] == "alpha"
    assert result.resolved["y"] == "beta"
    assert result.count() == 2
