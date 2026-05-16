"""Tests for confpatch.annotate."""
from __future__ import annotations

import pytest
from pathlib import Path

from confpatch.annotate import (
    AnnotateError,
    Annotation,
    add_annotation,
    get_annotation,
    load_annotations,
    remove_annotation,
    _annotations_path,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


def test_load_annotations_empty(config_file):
    result = load_annotations(config_file)
    assert result == {}


def test_add_annotation_returns_annotation(config_file):
    ann = add_annotation(config_file, "database.host", "Primary DB host", author="alice")
    assert isinstance(ann, Annotation)
    assert ann.key == "database.host"
    assert ann.note == "Primary DB host"
    assert ann.author == "alice"


def test_add_annotation_persists(config_file):
    add_annotation(config_file, "app.port", "Service port")
    loaded = load_annotations(config_file)
    assert "app.port" in loaded
    assert loaded["app.port"].note == "Service port"


def test_add_annotation_with_tags(config_file):
    ann = add_annotation(config_file, "feature.flag", "Toggle", tags=["beta", "infra"])
    assert ann.tags == ["beta", "infra"]
    loaded = load_annotations(config_file)
    assert loaded["feature.flag"].tags == ["beta", "infra"]


def test_add_annotation_overwrites_same_key(config_file):
    add_annotation(config_file, "key", "First note")
    add_annotation(config_file, "key", "Second note")
    loaded = load_annotations(config_file)
    assert loaded["key"].note == "Second note"


def test_add_annotation_empty_key_raises(config_file):
    with pytest.raises(AnnotateError, match="Key must not be empty"):
        add_annotation(config_file, "  ", "Some note")


def test_add_annotation_empty_note_raises(config_file):
    with pytest.raises(AnnotateError, match="Note must not be empty"):
        add_annotation(config_file, "some.key", "")


def test_get_annotation_returns_correct(config_file):
    add_annotation(config_file, "db.port", "Port number", author="bob")
    ann = get_annotation(config_file, "db.port")
    assert ann.key == "db.port"
    assert ann.author == "bob"


def test_get_annotation_missing_key_raises(config_file):
    with pytest.raises(AnnotateError, match="No annotation found"):
        get_annotation(config_file, "nonexistent.key")


def test_remove_annotation_removes_entry(config_file):
    add_annotation(config_file, "x.y", "note")
    remove_annotation(config_file, "x.y")
    loaded = load_annotations(config_file)
    assert "x.y" not in loaded


def test_remove_annotation_missing_key_raises(config_file):
    with pytest.raises(AnnotateError, match="No annotation found"):
        remove_annotation(config_file, "ghost.key")


def test_annotations_file_location(config_file):
    path = _annotations_path(config_file)
    assert path.name == ".config.yaml.annotations.json"
    assert path.parent == config_file.parent


def test_annotation_roundtrip():
    ann = Annotation(key="a.b", note="hello", author="dev", tags=["x"])
    restored = Annotation.from_dict(ann.to_dict())
    assert restored.key == ann.key
    assert restored.note == ann.note
    assert restored.author == ann.author
    assert restored.tags == ann.tags
