"""Tests for confpatch.diff module."""

import pytest
from confpatch.diff import compute_diff, format_diff


def test_compute_diff_no_changes():
    cfg = {"a": 1, "b": "hello"}
    assert compute_diff(cfg, cfg) == []


def test_compute_diff_added_key():
    original = {"a": 1}
    patched = {"a": 1, "b": 2}
    changes = compute_diff(original, patched)
    assert len(changes) == 1
    assert changes[0] == {"key": "b", "action": "added", "old": None, "new": 2}


def test_compute_diff_removed_key():
    original = {"a": 1, "b": 2}
    patched = {"a": 1}
    changes = compute_diff(original, patched)
    assert len(changes) == 1
    assert changes[0] == {"key": "b", "action": "removed", "old": 2, "new": None}


def test_compute_diff_changed_value():
    original = {"a": 1}
    patched = {"a": 99}
    changes = compute_diff(original, patched)
    assert changes[0]["action"] == "changed"
    assert changes[0]["old"] == 1
    assert changes[0]["new"] == 99


def test_compute_diff_nested():
    original = {"db": {"host": "localhost", "port": 5432}}
    patched = {"db": {"host": "remotehost", "port": 5432}}
    changes = compute_diff(original, patched)
    assert len(changes) == 1
    assert changes[0]["key"] == "db.host"
    assert changes[0]["action"] == "changed"


def test_compute_diff_nested_added():
    original = {"db": {"host": "localhost"}}
    patched = {"db": {"host": "localhost", "port": 5432}}
    changes = compute_diff(original, patched)
    assert changes[0]["key"] == "db.port"
    assert changes[0]["action"] == "added"


def test_format_diff_no_changes():
    assert format_diff([]) == "(no changes)"


def test_format_diff_added():
    changes = [{"key": "x", "action": "added", "old": None, "new": 42}]
    out = format_diff(changes)
    assert out.startswith("+")
    assert "x" in out
    assert "42" in out


def test_format_diff_removed():
    changes = [{"key": "y", "action": "removed", "old": "hello", "new": None}]
    out = format_diff(changes)
    assert out.startswith("-")


def test_format_diff_changed():
    changes = [{"key": "z", "action": "changed", "old": 1, "new": 2}]
    out = format_diff(changes)
    assert out.startswith("~")
    assert "->" in out


def test_format_diff_color_does_not_crash():
    changes = [
        {"key": "a", "action": "added", "old": None, "new": 1},
        {"key": "b", "action": "removed", "old": 2, "new": None},
        {"key": "c", "action": "changed", "old": 3, "new": 4},
    ]
    out = format_diff(changes, color=True)
    assert "a" in out and "b" in out and "c" in out
