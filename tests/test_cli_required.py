"""Tests for confpatch.cli_required."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from confpatch.cli_required import cmd_required


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("version: '1.0'\ndatabase:\n  host: localhost\n")
    return p


def make_args(config, keys):
    ns = argparse.Namespace()
    ns.config = str(config)
    ns.keys = keys
    return ns


def test_cmd_required_all_present(config_file):
    args = make_args(config_file, ["version", "database.host"])
    # Should not raise or exit
    with patch("sys.exit") as mock_exit:
        cmd_required(args)
        mock_exit.assert_not_called()


def test_cmd_required_missing_key_exits_2(config_file, capsys):
    args = make_args(config_file, ["version", "missing_key"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_required(args)
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "missing_key" in captured.out


def test_cmd_required_config_not_found(tmp_path, capsys):
    args = make_args(tmp_path / "nonexistent.yaml", ["key"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_required(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_required_no_keys_exits_1(config_file, capsys):
    args = make_args(config_file, [])
    with pytest.raises(SystemExit) as exc_info:
        cmd_required(args)
    assert exc_info.value.code == 1


def test_cmd_required_prints_summary(config_file, capsys):
    args = make_args(config_file, ["version"])
    with patch("sys.exit"):
        cmd_required(args)
    captured = capsys.readouterr()
    assert "present" in captured.out or "missing" in captured.out
