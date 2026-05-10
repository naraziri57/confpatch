"""Tests for confpatch.cli_condition."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from confpatch.cli_condition import cmd_apply_if


@pytest.fixture()
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"env": "production", "debug": False}))
    return p


@pytest.fixture()
def patch_file(tmp_path):
    p = tmp_path / "patch.yaml"
    p.write_text(yaml.dump({"debug": True}))
    return p


def make_args(config, patch, conditions, dry_run=False):
    return SimpleNamespace(
        config=str(config),
        patch=str(patch),
        conditions=json.dumps(conditions),
        dry_run=dry_run,
    )


def test_cmd_apply_if_conditions_met(config_file, patch_file):
    conditions = [{"key": "env", "op": "eq", "value": "production"}]
    args = make_args(config_file, patch_file, conditions)
    result = cmd_apply_if(args)
    assert result == 0
    updated = yaml.safe_load(config_file.read_text())
    assert updated["debug"] is True


def test_cmd_apply_if_conditions_not_met(config_file, patch_file):
    conditions = [{"key": "env", "op": "eq", "value": "staging"}]
    args = make_args(config_file, patch_file, conditions)
    result = cmd_apply_if(args)
    assert result == 0
    updated = yaml.safe_load(config_file.read_text())
    assert updated["debug"] is False  # patch was NOT applied


def test_cmd_apply_if_dry_run(config_file, patch_file):
    conditions = [{"key": "env", "op": "eq", "value": "production"}]
    args = make_args(config_file, patch_file, conditions, dry_run=True)
    result = cmd_apply_if(args)
    assert result == 0
    updated = yaml.safe_load(config_file.read_text())
    assert updated["debug"] is False  # dry run — file unchanged


def test_cmd_apply_if_config_not_found(tmp_path, patch_file):
    conditions = [{"key": "env", "op": "eq", "value": "production"}]
    args = make_args(tmp_path / "missing.yaml", patch_file, conditions)
    result = cmd_apply_if(args)
    assert result == 1


def test_cmd_apply_if_patch_not_found(config_file, tmp_path):
    conditions = [{"key": "env", "op": "eq", "value": "production"}]
    args = make_args(config_file, tmp_path / "missing.yaml", conditions)
    result = cmd_apply_if(args)
    assert result == 1


def test_cmd_apply_if_invalid_conditions_json(config_file, patch_file):
    args = SimpleNamespace(
        config=str(config_file),
        patch=str(patch_file),
        conditions="not valid json",
        dry_run=False,
    )
    result = cmd_apply_if(args)
    assert result == 1


def test_cmd_apply_if_single_condition_object(config_file, patch_file):
    """A single condition dict (not wrapped in list) should also work."""
    conditions = {"key": "env", "op": "eq", "value": "production"}
    args = make_args(config_file, patch_file, conditions)
    result = cmd_apply_if(args)
    assert result == 0
    updated = yaml.safe_load(config_file.read_text())
    assert updated["debug"] is True
