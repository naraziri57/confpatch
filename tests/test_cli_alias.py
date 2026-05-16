"""Tests for confpatch.cli_alias"""

import pytest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from confpatch.cli_alias import (
    cmd_alias_add,
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_resolve,
)
from confpatch.alias import add_alias


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "app.yaml"
    f.write_text("env: prod\n")
    return f


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_alias_add_success(config_file, capsys):
    args = make_args(config=str(config_file), name="fix", patch="patches/fix.yaml")
    rc = cmd_alias_add(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "fix" in out


def test_cmd_alias_add_config_not_found(tmp_path, capsys):
    args = make_args(config=str(tmp_path / "nope.yaml"), name="x", patch="p.yaml")
    rc = cmd_alias_add(args)
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def test_cmd_alias_add_empty_name_fails(config_file, capsys):
    args = make_args(config=str(config_file), name="", patch="p.yaml")
    rc = cmd_alias_add(args)
    assert rc == 1


def test_cmd_alias_remove_success(config_file, capsys):
    add_alias(config_file, "fix", "patches/fix.yaml")
    args = make_args(config=str(config_file), name="fix")
    rc = cmd_alias_remove(args)
    assert rc == 0
    assert "removed" in capsys.readouterr().out


def test_cmd_alias_remove_not_found(config_file, capsys):
    args = make_args(config=str(config_file), name="ghost")
    rc = cmd_alias_remove(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().out


def test_cmd_alias_list_empty(config_file, capsys):
    args = make_args(config=str(config_file))
    rc = cmd_alias_list(args)
    assert rc == 0
    assert "No aliases" in capsys.readouterr().out


def test_cmd_alias_list_shows_entries(config_file, capsys):
    add_alias(config_file, "prod", "patches/prod.yaml")
    args = make_args(config=str(config_file))
    rc = cmd_alias_list(args)
    assert rc == 0
    assert "prod" in capsys.readouterr().out


def test_cmd_alias_resolve_success(config_file, capsys):
    add_alias(config_file, "prod", "patches/prod.yaml")
    args = make_args(config=str(config_file), name="prod")
    rc = cmd_alias_resolve(args)
    assert rc == 0
    assert "patches/prod.yaml" in capsys.readouterr().out


def test_cmd_alias_resolve_missing(config_file, capsys):
    args = make_args(config=str(config_file), name="nope")
    rc = cmd_alias_resolve(args)
    assert rc == 1
