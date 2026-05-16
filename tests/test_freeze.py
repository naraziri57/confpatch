"""Tests for confpatch.freeze module."""

import json
import pytest
from pathlib import Path

from confpatch.freeze import (
    FreezeError,
    FreezeStore,
    freeze_key,
    unfreeze_key,
    filter_frozen_keys,
    load_freeze_store,
    _freeze_path,
)


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("key: value\n")
    return p


def test_load_freeze_store_empty(config_file):
    store = load_freeze_store(config_file)
    assert store.frozen_keys == []
    assert store.config_path == config_file


def test_freeze_key_adds_to_store(config_file):
    store = freeze_key(config_file, "database.host")
    assert "database.host" in store.frozen_keys


def test_freeze_key_persists(config_file):
    freeze_key(config_file, "api_key")
    store = load_freeze_store(config_file)
    assert "api_key" in store.frozen_keys


def test_freeze_key_no_duplicates(config_file):
    freeze_key(config_file, "port")
    freeze_key(config_file, "port")
    store = load_freeze_store(config_file)
    assert store.frozen_keys.count("port") == 1


def test_freeze_key_file_not_found(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FreezeError, match="not found"):
        freeze_key(missing, "key")


def test_unfreeze_key_removes_key(config_file):
    freeze_key(config_file, "host")
    store = unfreeze_key(config_file, "host")
    assert "host" not in store.frozen_keys


def test_unfreeze_key_not_frozen_raises(config_file):
    with pytest.raises(FreezeError, match="not frozen"):
        unfreeze_key(config_file, "nonexistent")


def test_filter_frozen_keys_removes_frozen(config_file):
    freeze_key(config_file, "password")
    store = load_freeze_store(config_file)
    patch = {"password": "new_secret", "host": "localhost"}
    filtered, skipped = filter_frozen_keys(patch, store)
    assert "password" not in filtered
    assert "host" in filtered
    assert "password" in skipped


def test_filter_frozen_keys_no_frozen(config_file):
    store = load_freeze_store(config_file)
    patch = {"a": 1, "b": 2}
    filtered, skipped = filter_frozen_keys(patch, store)
    assert filtered == patch
    assert skipped == []


def test_freeze_store_to_dict(config_file):
    store = FreezeStore(config_path=config_file, frozen_keys=["x", "y"])
    d = store.to_dict()
    assert d["frozen"] == ["x", "y"]
    assert "config" in d


def test_freeze_path_location(config_file):
    fp = _freeze_path(config_file)
    assert fp.parent == config_file.parent
    assert fp.name == ".config.freeze.json"
