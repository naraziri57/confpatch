"""Tests for confpatch.alias"""

import pytest
from pathlib import Path

from confpatch.alias import (
    AliasError,
    AliasStore,
    add_alias,
    list_aliases,
    load_aliases,
    remove_alias,
    resolve_alias,
    _alias_path,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


def test_load_aliases_empty(config_file):
    store = load_aliases(config_file)
    assert store.aliases == {}


def test_add_alias_creates_entry(config_file):
    store = add_alias(config_file, "myfix", "patches/fix.yaml")
    assert "myfix" in store.aliases
    assert store.aliases["myfix"] == "patches/fix.yaml"


def test_add_alias_persists(config_file):
    add_alias(config_file, "myfix", "patches/fix.yaml")
    store = load_aliases(config_file)
    assert store.aliases["myfix"] == "patches/fix.yaml"


def test_add_alias_empty_name_raises(config_file):
    with pytest.raises(AliasError, match="empty"):
        add_alias(config_file, "  ", "patches/fix.yaml")


def test_add_alias_overwrites_existing(config_file):
    add_alias(config_file, "myfix", "patches/old.yaml")
    add_alias(config_file, "myfix", "patches/new.yaml")
    store = load_aliases(config_file)
    assert store.aliases["myfix"] == "patches/new.yaml"


def test_remove_alias_success(config_file):
    add_alias(config_file, "myfix", "patches/fix.yaml")
    store = remove_alias(config_file, "myfix")
    assert "myfix" not in store.aliases


def test_remove_alias_not_found_raises(config_file):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(config_file, "ghost")


def test_resolve_alias_returns_path(config_file):
    add_alias(config_file, "prod", "patches/prod.yaml")
    result = resolve_alias(config_file, "prod")
    assert result == "patches/prod.yaml"


def test_resolve_alias_missing_raises(config_file):
    with pytest.raises(AliasError, match="not defined"):
        resolve_alias(config_file, "missing")


def test_list_aliases_sorted(config_file):
    add_alias(config_file, "zzz", "z.yaml")
    add_alias(config_file, "aaa", "a.yaml")
    entries = list_aliases(config_file)
    names = [n for n, _ in entries]
    assert names == sorted(names)


def test_alias_store_roundtrip():
    store = AliasStore(aliases={"a": "a.yaml", "b": "b.yaml"})
    restored = AliasStore.from_dict(store.to_dict())
    assert restored.aliases == store.aliases


def test_alias_path_location(config_file):
    path = _alias_path(config_file)
    assert path.parent == config_file.parent
    assert path.name == ".config_aliases.json"
