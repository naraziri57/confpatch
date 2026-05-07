"""Tests for confpatch.watch."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from confpatch.watch import get_mtime, watch_file, make_patch_callback, WatchError


# ---------------------------------------------------------------------------
# get_mtime
# ---------------------------------------------------------------------------

def test_get_mtime_returns_float(tmp_path):
    f = tmp_path / "cfg.yaml"
    f.write_text("a: 1")
    mtime = get_mtime(f)
    assert isinstance(mtime, float)
    assert mtime > 0


def test_get_mtime_missing_file(tmp_path):
    with pytest.raises(WatchError, match="not found"):
        get_mtime(tmp_path / "ghost.yaml")


# ---------------------------------------------------------------------------
# watch_file
# ---------------------------------------------------------------------------

def test_watch_file_calls_callback_on_change(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("a: 1")

    callback = MagicMock()
    mtimes = [1000.0, 1000.0, 1001.0]  # change on third poll

    with patch("confpatch.watch.get_mtime", side_effect=mtimes), \
         patch("confpatch.watch.time.sleep"):
        watch_file(cfg, callback, interval=0.1, max_events=1)

    callback.assert_called_once_with(cfg)


def test_watch_file_no_change_no_callback(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("a: 1")

    callback = MagicMock()
    # same mtime every call — we need to break the loop somehow;
    # use max_events=0 trick: never fires, but sleep will be called once
    with patch("confpatch.watch.get_mtime", return_value=1000.0), \
         patch("confpatch.watch.time.sleep") as mock_sleep:
        # Patch to stop after 2 sleeps by raising KeyboardInterrupt
        mock_sleep.side_effect = [None, KeyboardInterrupt]
        watch_file(cfg, callback, interval=0.1)

    callback.assert_not_called()


def test_watch_file_raises_watch_error_on_missing_file(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("a: 1")

    with patch("confpatch.watch.get_mtime", side_effect=[1000.0, WatchError("gone")]), \
         patch("confpatch.watch.time.sleep"):
        with pytest.raises(WatchError, match="gone"):
            watch_file(cfg, MagicMock(), interval=0.1)


# ---------------------------------------------------------------------------
# make_patch_callback
# ---------------------------------------------------------------------------

def test_make_patch_callback_applies_patch(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    patch_file = tmp_path / "patch.yaml"

    cfg.write_text("a: 1\nb: 2\n")
    patch_file.write_text("b: 99\n")

    from confpatch.loaders import load_config

    callback = make_patch_callback(patch_file)
    callback(cfg)

    result = load_config(cfg)
    assert result["b"] == 99
    assert result["a"] == 1


def test_make_patch_callback_calls_on_apply_hook(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    patch_file = tmp_path / "patch.yaml"

    cfg.write_text("x: 10\n")
    patch_file.write_text("x: 20\n")

    hook = MagicMock()
    callback = make_patch_callback(patch_file, on_apply=hook)
    callback(cfg)

    hook.assert_called_once()
    called_path, called_result = hook.call_args[0]
    assert called_path == cfg
    assert called_result["x"] == 20
