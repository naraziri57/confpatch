"""Tests for confpatch.hooks."""

import sys
from pathlib import Path

import pytest

from confpatch.hooks import (
    HookConfig,
    HookError,
    HookResult,
    _run_command,
    load_hooks,
    run_hooks,
)


def test_run_command_success():
    result = _run_command("echo hello")
    assert result.ok
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_run_command_failure():
    result = _run_command("exit 1", cwd=Path("."))
    assert not result.ok
    assert result.returncode != 0


def test_run_command_captures_stdout():
    result = _run_command("echo confpatch")
    assert result.stdout == "confpatch"


def test_hook_result_ok_true():
    r = HookResult(command="echo", returncode=0, stdout="", stderr="")
    assert r.ok is True


def test_hook_result_ok_false():
    r = HookResult(command="false", returncode=1, stdout="", stderr="error")
    assert r.ok is False


def test_run_hooks_all_succeed():
    results = run_hooks(["echo a", "echo b"])
    assert len(results) == 2
    assert all(r.ok for r in results)


def test_run_hooks_empty_list():
    results = run_hooks([])
    assert results == []


def test_run_hooks_raises_on_failure():
    with pytest.raises(HookError, match="Hook command failed"):
        run_hooks(["echo ok", "exit 2"])


def test_run_hooks_stops_on_first_failure():
    results = []
    with pytest.raises(HookError):
        results = run_hooks(["exit 1", "echo never"])
    # Only the failing command should have run
    assert len(results) == 0


def test_load_hooks_valid():
    config = {"hooks": {"pre": ["echo pre"], "post": ["echo post"]}}
    hc = load_hooks(config)
    assert isinstance(hc, HookConfig)
    assert hc.pre == ["echo pre"]
    assert hc.post == ["echo post"]


def test_load_hooks_empty():
    hc = load_hooks({})
    assert hc.pre == []
    assert hc.post == []


def test_load_hooks_invalid_type():
    with pytest.raises(HookError, match="must be a mapping"):
        load_hooks({"hooks": "bad"})


def test_load_hooks_invalid_pre_type():
    with pytest.raises(HookError, match="must be lists"):
        load_hooks({"hooks": {"pre": "not-a-list", "post": []}})
