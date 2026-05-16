"""Tests for confpatch.cli_pipeline."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from confpatch.cli_pipeline import cmd_pipeline, register_pipeline_commands


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"version": "1.0", "debug": False}))
    return cfg


@pytest.fixture()
def patch_file(tmp_path: Path) -> Path:
    p = tmp_path / "patch.yaml"
    p.write_text(yaml.dump({"version": "2.0"}))
    return p


def make_args(**kwargs):
    defaults = {"dry_run": False}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_pipeline_success(config_file: Path, patch_file: Path, tmp_path: Path) -> None:
    steps = [{"name": "bump", "type": "patch", "patch_file": str(patch_file)}]
    steps_file = tmp_path / "steps.json"
    steps_file.write_text(json.dumps(steps))
    args = make_args(config=str(config_file), steps_file=str(steps_file))
    rc = cmd_pipeline(args)
    assert rc == 0


def test_cmd_pipeline_steps_file_not_found(config_file: Path) -> None:
    args = make_args(config=str(config_file), steps_file="/no/such/steps.json")
    rc = cmd_pipeline(args)
    assert rc == 1


def test_cmd_pipeline_invalid_json(config_file: Path, tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json {{")
    args = make_args(config=str(config_file), steps_file=str(bad))
    rc = cmd_pipeline(args)
    assert rc == 1


def test_cmd_pipeline_steps_not_list(config_file: Path, tmp_path: Path) -> None:
    steps_file = tmp_path / "steps.json"
    steps_file.write_text(json.dumps({"step": "oops"}))
    args = make_args(config=str(config_file), steps_file=str(steps_file))
    rc = cmd_pipeline(args)
    assert rc == 1


def test_cmd_pipeline_config_not_found(tmp_path: Path) -> None:
    steps_file = tmp_path / "steps.json"
    steps_file.write_text(json.dumps([]))
    args = make_args(config=str(tmp_path / "missing.yaml"), steps_file=str(steps_file))
    rc = cmd_pipeline(args)
    assert rc == 1


def test_cmd_pipeline_dry_run(config_file: Path, patch_file: Path, tmp_path: Path) -> None:
    original = config_file.read_text()
    steps = [{"name": "bump", "type": "patch", "patch_file": str(patch_file)}]
    steps_file = tmp_path / "steps.json"
    steps_file.write_text(json.dumps(steps))
    args = make_args(config=str(config_file), steps_file=str(steps_file), dry_run=True)
    rc = cmd_pipeline(args)
    assert rc == 0
    assert config_file.read_text() == original


def test_register_pipeline_commands() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_pipeline_commands(sub)
    args = parser.parse_args(["pipeline", "cfg.yaml", "steps.json", "--dry-run"])
    assert args.config == "cfg.yaml"
    assert args.steps_file == "steps.json"
    assert args.dry_run is True
