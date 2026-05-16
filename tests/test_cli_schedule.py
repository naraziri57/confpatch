"""Tests for confpatch.cli_schedule."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from confpatch.cli_schedule import cmd_schedule, register_schedule_commands
from confpatch.schedule import ScheduleResult


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"config": "c.yaml", "patch": "p.yaml", "after": None, "at": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return str(f)


@pytest.fixture()
def patch_file(tmp_path):
    f = tmp_path / "patch.yaml"
    f.write_text("key: updated\n")
    return str(f)


def test_cmd_schedule_config_not_found(patch_file):
    args = make_args(config="nonexistent.yaml", patch=patch_file)
    rc = cmd_schedule(args)
    assert rc == 1


def test_cmd_schedule_patch_not_found(config_file):
    args = make_args(config=config_file, patch="missing.yaml")
    rc = cmd_schedule(args)
    assert rc == 1


def test_cmd_schedule_no_timing(config_file, patch_file):
    args = make_args(config=config_file, patch=patch_file)
    rc = cmd_schedule(args)
    assert rc == 1


def test_cmd_schedule_after_success(config_file, patch_file):
    good_result = ScheduleResult(
        config_file=config_file,
        patch_file=patch_file,
        ran_at=datetime.now(),
        success=True,
        message="patch applied",
    )
    args = make_args(config=config_file, patch=patch_file, after=0.0)
    with patch("confpatch.cli_schedule.run_after", return_value=good_result):
        rc = cmd_schedule(args)
    assert rc == 0


def test_cmd_schedule_after_failure(config_file, patch_file):
    bad_result = ScheduleResult(
        config_file=config_file,
        patch_file=patch_file,
        ran_at=datetime.now(),
        success=False,
        message="oops",
    )
    args = make_args(config=config_file, patch=patch_file, after=0.0)
    with patch("confpatch.cli_schedule.run_after", return_value=bad_result):
        rc = cmd_schedule(args)
    assert rc == 1


def test_cmd_schedule_at_success(config_file, patch_file):
    future = (datetime.now() + timedelta(seconds=60)).isoformat()
    good_result = ScheduleResult(
        config_file=config_file,
        patch_file=patch_file,
        ran_at=datetime.now(),
        success=True,
        message="patch applied",
    )
    args = make_args(config=config_file, patch=patch_file, at=future)
    with patch("confpatch.cli_schedule.run_at", return_value=good_result):
        rc = cmd_schedule(args)
    assert rc == 0


def test_register_schedule_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_schedule_commands(sub)
    parsed = parser.parse_args(["schedule", "c.yaml", "p.yaml", "--after", "5"])
    assert parsed.after == 5.0
    assert parsed.config == "c.yaml"
