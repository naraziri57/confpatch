"""Tests for confpatch.pin — key pinning feature."""

import json
import pytest
from pathlib import Path

from confpatch.pin import (
    PinStore,
    PinError,
    load_pins,
    save_pins,
    pin_key,
    unpin_key,
    filter_pinned,
    _pin_path,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


def test_load_pins_empty(config_file):
    store = load_pins(config_file)
    assert store.pinned == set()


def test_save_and_load_pins(config_file):
    store = PinStore(pinned={"database.host", "app.secret"})
    save_pins(config_file, store)
    loaded = load_pins(config_file)
    assert loaded.pinned == {"database.host", "app.secret"}


def test_pin_path_location(config_file):
    pin_file = _pin_path(config_file)
    assert pin_file.name == "config.yaml.pins"
    assert pin_file.parent == config_file.parent


def test_pin_key_adds_to_store(config_file):
    store = pin_key(config_file, "database.host")
    assert "database.host" in store.pinned


def test_pin_key_persists(config_file):
    pin_key(config_file, "app.secret")
    store = load_pins(config_file)
    assert "app.secret" in store.pinned


def test_unpin_key_removes(config_file):
    pin_key(config_file, "database.host")
    store = unpin_key(config_file, "database.host")
    assert "database.host" not in store.pinned


def test_unpin_key_missing_is_safe(config_file):
    store = unpin_key(config_file, "nonexistent.key")
    assert "nonexistent.key" not in store.pinned


def test_filter_pinned_removes_pinned_keys(config_file):
    store = PinStore(pinned={"host", "secret"})
    patch = {"host": "newhost", "secret": "newsecret", "port": 9090}
    filtered, skipped = filter_pinned(patch, store)
    assert filtered == {"port": 9090}
    assert set(skipped) == {"host", "secret"}


def test_filter_pinned_no_overlap(config_file):
    store = PinStore(pinned={"locked_key"})
    patch = {"free_key": 42}
    filtered, skipped = filter_pinned(patch, store)
    assert filtered == {"free_key": 42}
    assert skipped == []


def test_load_pins_corrupt_file_raises(config_file):
    pin_file = _pin_path(config_file)
    pin_file.write_text("not json{{{")
    with pytest.raises(PinError):
        load_pins(config_file)


def test_pin_store_to_dict_sorted():
    store = PinStore(pinned={"z_key", "a_key", "m_key"})
    d = store.to_dict()
    assert d["pinned"] == ["a_key", "m_key", "z_key"]
