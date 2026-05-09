"""Tests for confpatch.cli_chain."""

from __future__ import annotations

import argparse
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from confpatch.cli_chain import cmd_chain, register_chain_commands
from confpatch.chain import ChainResult, ChainError


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": "config.yaml",
        "patches": ["p1.yaml"],
        "format": None,
        "keep_going": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_chain_success(capsys):
    result = ChainResult(
        config_file="cfg.yaml",
        patches_applied=["p1.yaml"],
        patches_failed=[],
        final_config={"k": "v"},
    )
    with patch("confpatch.cli_chain.apply_chain", return_value=result):
        cmd_chain(make_args())
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "p1.yaml" in out


def test_cmd_chain_no_patches(capsys):
    cmd_chain(make_args(patches=[]))
    out = capsys.readouterr().out
    assert "No patch files" in out


def test_cmd_chain_error(capsys):
    with patch("confpatch.cli_chain.apply_chain", side_effect=ChainError("boom")):
        cmd_chain(make_args())
    out = capsys.readouterr().out
    assert "Error" in out
    assert "boom" in out


def test_cmd_chain_failed_patch_shown(capsys):
    result = ChainResult(
        config_file="cfg.yaml",
        patches_applied=[],
        patches_failed=[("bad.yaml", "invalid")],
        final_config={},
    )
    with patch("confpatch.cli_chain.apply_chain", return_value=result):
        cmd_chain(make_args(patches=["bad.yaml"]))
    out = capsys.readouterr().out
    assert "[fail]" in out
    assert "bad.yaml" in out


def test_cmd_chain_dry_run_message(capsys):
    result = ChainResult(
        config_file="cfg.yaml",
        patches_applied=["p1.yaml"],
        patches_failed=[],
        final_config={},
    )
    with patch("confpatch.cli_chain.apply_chain", return_value=result):
        cmd_chain(make_args(dry_run=True))
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_register_chain_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_chain_commands(subparsers)
    args = parser.parse_args(["chain", "cfg.yaml", "p1.yaml", "p2.yaml"])
    assert args.config == "cfg.yaml"
    assert args.patches == ["p1.yaml", "p2.yaml"]
