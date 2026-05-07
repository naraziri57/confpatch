"""Tests for confpatch.cli_profile."""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from confpatch.cli_profile import (
    cmd_profile_apply,
    cmd_profile_delete,
    cmd_profile_list,
    cmd_profile_save,
)
from confpatch.profile import save_profile, Profile


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"name": "test", "store": "", "dry_run": False,
                "description": "", "tags": [], "patch": "", "config": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "store"


@pytest.fixture
def patch_file(tmp_path: Path) -> Path:
    p = tmp_path / "patch.json"
    p.write_text(json.dumps({"debug": True}))
    return p


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    import yaml
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"debug": False, "host": "localhost"}))
    return p


def test_cmd_profile_save_success(store, patch_file):
    args = make_args(name="ci", patch=str(patch_file), store=str(store))
    assert cmd_profile_save(args) == 0
    assert (store / "profiles.json").exists()


def test_cmd_profile_save_bad_patch(store, tmp_path):
    args = make_args(name="ci", patch=str(tmp_path / "nope.json"), store=str(store))
    assert cmd_profile_save(args) == 1


def test_cmd_profile_list_empty(store):
    args = make_args(store=str(store))
    assert cmd_profile_list(args) == 0


def test_cmd_profile_list_with_profiles(store):
    save_profile(Profile("dev", {"x": 1}, "dev env", ["dev"]), store)
    args = make_args(store=str(store))
    assert cmd_profile_list(args) == 0


def test_cmd_profile_apply_success(store, config_file):
    save_profile(Profile("prod", {"debug": True}), store)
    args = make_args(name="prod", config=str(config_file), store=str(store))
    assert cmd_profile_apply(args) == 0


def test_cmd_profile_apply_dry_run(store, config_file):
    save_profile(Profile("prod", {"debug": True}), store)
    args = make_args(name="prod", config=str(config_file), store=str(store), dry_run=True)
    assert cmd_profile_apply(args) == 0


def test_cmd_profile_apply_not_found(store, config_file):
    args = make_args(name="ghost", config=str(config_file), store=str(store))
    assert cmd_profile_apply(args) == 1


def test_cmd_profile_delete_success(store):
    save_profile(Profile("old", {}), store)
    args = make_args(name="old", store=str(store))
    assert cmd_profile_delete(args) == 0


def test_cmd_profile_delete_not_found(store):
    args = make_args(name="ghost", store=str(store))
    assert cmd_profile_delete(args) == 1
