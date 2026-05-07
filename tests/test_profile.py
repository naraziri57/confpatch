"""Tests for confpatch.profile."""

from __future__ import annotations

import pytest
from pathlib import Path

from confpatch.profile import (
    Profile,
    ProfileError,
    delete_profile,
    get_profile,
    load_profiles,
    save_profile,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "profiles"


def make_profile(name: str = "default", patch: dict | None = None) -> Profile:
    return Profile(name=name, patch=patch or {"key": "value"}, description="test", tags=["ci"])


def test_load_profiles_empty(store: Path):
    assert load_profiles(store) == []


def test_save_and_load_profile(store: Path):
    p = make_profile()
    save_profile(p, store)
    profiles = load_profiles(store)
    assert len(profiles) == 1
    assert profiles[0].name == "default"
    assert profiles[0].patch == {"key": "value"}


def test_save_profile_overwrites_same_name(store: Path):
    save_profile(make_profile("dev", {"x": 1}), store)
    save_profile(make_profile("dev", {"x": 99}), store)
    profiles = load_profiles(store)
    assert len(profiles) == 1
    assert profiles[0].patch == {"x": 99}


def test_save_multiple_profiles(store: Path):
    save_profile(make_profile("a"), store)
    save_profile(make_profile("b"), store)
    assert len(load_profiles(store)) == 2


def test_get_profile_found(store: Path):
    save_profile(make_profile("prod"), store)
    p = get_profile("prod", store)
    assert p.name == "prod"


def test_get_profile_not_found(store: Path):
    with pytest.raises(ProfileError, match="not found"):
        get_profile("nonexistent", store)


def test_delete_profile(store: Path):
    save_profile(make_profile("staging"), store)
    delete_profile("staging", store)
    assert load_profiles(store) == []


def test_delete_profile_not_found(store: Path):
    with pytest.raises(ProfileError, match="not found"):
        delete_profile("ghost", store)


def test_profile_to_dict_round_trip():
    p = Profile(name="x", patch={"a": 1}, description="desc", tags=["t1"])
    d = p.to_dict()
    p2 = Profile.from_dict(d)
    assert p2.name == p.name
    assert p2.patch == p.patch
    assert p2.description == p.description
    assert p2.tags == p.tags


def test_profile_tags_default_empty():
    p = Profile(name="y", patch={})
    assert p.tags == []


def test_load_profiles_invalid_json(store: Path):
    store.mkdir(parents=True)
    (store / "profiles.json").write_text("not json")
    with pytest.raises(ProfileError):
        load_profiles(store)
