"""Tests for confpatch.preset"""

import pytest
from pathlib import Path

from confpatch.preset import (
    Preset,
    PresetError,
    delete_preset,
    get_preset,
    load_presets,
    save_preset,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("host: localhost\nport: 8080\n")
    return f


def test_load_presets_empty(config_file):
    result = load_presets(config_file)
    assert result == {}


def test_save_and_load_preset(config_file):
    preset = Preset(name="dev", patch={"host": "devhost"}, description="Dev env")
    save_preset(config_file, preset)
    loaded = load_presets(config_file)
    assert "dev" in loaded
    assert loaded["dev"].patch == {"host": "devhost"}
    assert loaded["dev"].description == "Dev env"


def test_save_preset_overwrites_same_name(config_file):
    save_preset(config_file, Preset(name="env", patch={"port": 9000}))
    save_preset(config_file, Preset(name="env", patch={"port": 9999}))
    loaded = load_presets(config_file)
    assert loaded["env"].patch["port"] == 9999


def test_save_preset_empty_name_raises(config_file):
    with pytest.raises(PresetError, match="empty"):
        save_preset(config_file, Preset(name="", patch={"x": 1}))


def test_save_preset_non_dict_patch_raises(config_file):
    with pytest.raises(PresetError, match="dict"):
        save_preset(config_file, Preset(name="bad", patch="not-a-dict"))


def test_get_preset_existing(config_file):
    save_preset(config_file, Preset(name="prod", patch={"debug": False}))
    p = get_preset(config_file, "prod")
    assert p.name == "prod"
    assert p.patch == {"debug": False}


def test_get_preset_missing_raises(config_file):
    with pytest.raises(PresetError, match="not found"):
        get_preset(config_file, "nonexistent")


def test_delete_preset(config_file):
    save_preset(config_file, Preset(name="tmp", patch={"x": 1}))
    delete_preset(config_file, "tmp")
    assert "tmp" not in load_presets(config_file)


def test_delete_preset_missing_raises(config_file):
    with pytest.raises(PresetError, match="not found"):
        delete_preset(config_file, "ghost")


def test_preset_with_tags(config_file):
    preset = Preset(name="tagged", patch={"a": 1}, tags=["infra", "prod"])
    save_preset(config_file, preset)
    loaded = get_preset(config_file, "tagged")
    assert loaded.tags == ["infra", "prod"]


def test_preset_to_dict_roundtrip():
    p = Preset(name="x", patch={"k": "v"}, description="desc", tags=["t1"])
    restored = Preset.from_dict(p.to_dict())
    assert restored.name == p.name
    assert restored.patch == p.patch
    assert restored.description == p.description
    assert restored.tags == p.tags
