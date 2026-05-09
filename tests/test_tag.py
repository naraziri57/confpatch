"""Tests for confpatch.tag module."""

from __future__ import annotations

from pathlib import Path
import pytest

from confpatch.tag import (
    TagError,
    TagStore,
    add_tag,
    remove_tag,
    get_patches_for_tag,
    list_tags,
    load_tags,
    _tag_path,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


def test_load_tags_empty(config_file):
    store = load_tags(config_file)
    assert store.tags == {}


def test_add_tag_creates_entry(config_file):
    store = add_tag(config_file, "release", "patches/v1.yaml")
    assert "release" in store.tags
    assert "patches/v1.yaml" in store.tags["release"]


def test_add_tag_persists(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    store = load_tags(config_file)
    assert "patches/v1.yaml" in store.tags["release"]


def test_add_tag_no_duplicates(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    add_tag(config_file, "release", "patches/v1.yaml")
    store = load_tags(config_file)
    assert store.tags["release"].count("patches/v1.yaml") == 1


def test_add_multiple_patches_to_tag(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    add_tag(config_file, "release", "patches/v2.yaml")
    store = load_tags(config_file)
    assert len(store.tags["release"]) == 2


def test_remove_tag_entirely(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    remove_tag(config_file, "release")
    store = load_tags(config_file)
    assert "release" not in store.tags


def test_remove_tag_specific_patch(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    add_tag(config_file, "release", "patches/v2.yaml")
    remove_tag(config_file, "release", "patches/v1.yaml")
    store = load_tags(config_file)
    assert "patches/v1.yaml" not in store.tags["release"]
    assert "patches/v2.yaml" in store.tags["release"]


def test_remove_tag_cleans_empty_list(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    remove_tag(config_file, "release", "patches/v1.yaml")
    store = load_tags(config_file)
    assert "release" not in store.tags


def test_remove_nonexistent_tag_raises(config_file):
    with pytest.raises(TagError, match="not found"):
        remove_tag(config_file, "nonexistent")


def test_remove_nonexistent_patch_raises(config_file):
    add_tag(config_file, "release", "patches/v1.yaml")
    with pytest.raises(TagError, match="not found"):
        remove_tag(config_file, "release", "patches/missing.yaml")


def test_get_patches_for_tag(config_file):
    add_tag(config_file, "hotfix", "patches/fix.yaml")
    patches = get_patches_for_tag(config_file, "hotfix")
    assert patches == ["patches/fix.yaml"]


def test_get_patches_for_missing_tag_raises(config_file):
    with pytest.raises(TagError, match="not found"):
        get_patches_for_tag(config_file, "ghost")


def test_list_tags_empty(config_file):
    assert list_tags(config_file) == []


def test_list_tags_sorted(config_file):
    add_tag(config_file, "zebra", "p.yaml")
    add_tag(config_file, "alpha", "p.yaml")
    assert list_tags(config_file) == ["alpha", "zebra"]


def test_tag_store_roundtrip():
    store = TagStore(tags={"rel": ["a.yaml", "b.yaml"]})
    restored = TagStore.from_dict(store.to_dict())
    assert restored.tags == store.tags


def test_tag_file_location(config_file):
    path = _tag_path(config_file)
    assert path.name == ".config_tags.json"
    assert path.parent == config_file.parent
