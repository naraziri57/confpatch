"""Tests for confpatch.cli_group."""

import sys
import types
import pytest

from confpatch.cli_group import cmd_group


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("host: localhost\nport: 5432\ndebug: true\n")
    return p


def make_args(**kwargs):
    defaults = {
        "config": "",
        "keys": [],
        "group": "",
        "overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    ns = types.SimpleNamespace(**defaults)
    return ns


def test_cmd_group_config_not_found(tmp_path, capsys):
    args = make_args(config=str(tmp_path / "missing.yaml"), keys=["host"], group="db")
    with pytest.raises(SystemExit) as exc:
        cmd_group(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_group_no_keys(config_file, capsys):
    args = make_args(config=str(config_file), keys=[], group="db")
    with pytest.raises(SystemExit) as exc:
        cmd_group(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "no keys" in captured.err.lower()


def test_cmd_group_no_group(config_file, capsys):
    args = make_args(config=str(config_file), keys=["host"], group="")
    with pytest.raises(SystemExit) as exc:
        cmd_group(args)
    assert exc.value.code == 1


def test_cmd_group_success(config_file, capsys):
    args = make_args(config=str(config_file), keys=["host", "port"], group="database")
    cmd_group(args)
    content = config_file.read_text()
    assert "database" in content
    captured = capsys.readouterr()
    assert "Grouped" in captured.out or "Saved" in captured.out


def test_cmd_group_dry_run_does_not_write(config_file, capsys):
    original = config_file.read_text()
    args = make_args(
        config=str(config_file), keys=["host"], group="db", dry_run=True
    )
    cmd_group(args)
    assert config_file.read_text() == original
    captured = capsys.readouterr()
    assert "Dry run" in captured.out


def test_cmd_group_missing_key_exits(config_file, capsys):
    args = make_args(config=str(config_file), keys=["nonexistent"], group="db")
    with pytest.raises(SystemExit) as exc:
        cmd_group(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Group error" in captured.err
