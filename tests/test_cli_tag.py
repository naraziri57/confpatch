"""Tests for confpatch.cli_tag module."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import pytest

from confpatch.tag import add_tag
from confpatch.cli_tag import (
    cmd_tag_add,
    cmd_tag_remove,
    cmd_tag_list,
    cmd_tag_show,
)


@pytest.fixture
def config_file(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_tag_add_success(config_file):
    args = make_args(config=str(config_file), tag="release", patch="p.yaml")
    rc = cmd_tag_add(args)
    assert rc == 0


def test_cmd_tag_add_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"), tag="t", patch="p.yaml")
    rc = cmd_tag_add(args)
    assert rc == 1


def test_cmd_tag_remove_success(config_file):
    add_tag(config_file, "release", "p.yaml")
    args = make_args(config=str(config_file), tag="release", patch=None)
    rc = cmd_tag_remove(args)
    assert rc == 0


def test_cmd_tag_remove_missing_tag(config_file):
    args = make_args(config=str(config_file), tag="ghost", patch=None)
    rc = cmd_tag_remove(args)
    assert rc == 1


def test_cmd_tag_remove_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"), tag="t", patch=None)
    rc = cmd_tag_remove(args)
    assert rc == 1


def test_cmd_tag_list_empty(config_file, capsys):
    args = make_args(config=str(config_file))
    rc = cmd_tag_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_list_shows_tags(config_file, capsys):
    add_tag(config_file, "hotfix", "p.yaml")
    args = make_args(config=str(config_file))
    rc = cmd_tag_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "hotfix" in out


def test_cmd_tag_list_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"))
    rc = cmd_tag_list(args)
    assert rc == 1


def test_cmd_tag_show_success(config_file, capsys):
    add_tag(config_file, "release", "patches/v1.yaml")
    args = make_args(config=str(config_file), tag="release")
    rc = cmd_tag_show(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "patches/v1.yaml" in out


def test_cmd_tag_show_missing_tag(config_file):
    args = make_args(config=str(config_file), tag="ghost")
    rc = cmd_tag_show(args)
    assert rc == 1


def test_cmd_tag_show_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"), tag="t")
    rc = cmd_tag_show(args)
    assert rc == 1
