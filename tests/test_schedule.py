"""Tests for confpatch.schedule."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from confpatch.schedule import ScheduleError, ScheduleResult, _execute, run_after, run_at


def _ok_fn(config: str, patch_file: str) -> None:
    pass


def _fail_fn(config: str, patch_file: str) -> None:
    raise RuntimeError("boom")


# --- _execute ---

def test_execute_success():
    result = _execute("config.yaml", "patch.yaml", _ok_fn)
    assert isinstance(result, ScheduleResult)
    assert result.success is True
    assert result.message == "patch applied"


def test_execute_failure():
    result = _execute("config.yaml", "patch.yaml", _fail_fn)
    assert result.success is False
    assert "boom" in result.message


def test_execute_stores_files():
    result = _execute("my.yaml", "my_patch.yaml", _ok_fn)
    assert result.config_file == "my.yaml"
    assert result.patch_file == "my_patch.yaml"


# --- run_after ---

def test_run_after_zero_delay():
    with patch("confpatch.schedule.time.sleep") as mock_sleep:
        result = run_after(0, "c.yaml", "p.yaml", _ok_fn)
    mock_sleep.assert_called_once_with(0)
    assert result.success is True


def test_run_after_negative_raises():
    with pytest.raises(ScheduleError, match="non-negative"):
        run_after(-1, "c.yaml", "p.yaml", _ok_fn)


def test_run_after_calls_sleep_with_correct_delay():
    with patch("confpatch.schedule.time.sleep") as mock_sleep:
        run_after(5.5, "c.yaml", "p.yaml", _ok_fn)
    mock_sleep.assert_called_once_with(5.5)


# --- run_at ---

def test_run_at_future_time():
    future = datetime.now() + timedelta(seconds=2)
    with patch("confpatch.schedule.time.sleep") as mock_sleep:
        with patch("confpatch.schedule.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.now()
            result = run_at(future, "c.yaml", "p.yaml", _ok_fn)
    assert result.success is True


def test_run_at_past_raises():
    past = datetime(2000, 1, 1)
    with pytest.raises(ScheduleError, match="past"):
        run_at(past, "c.yaml", "p.yaml", _ok_fn)


# --- ScheduleResult.summary ---

def test_summary_success():
    r = ScheduleResult(
        config_file="app.yaml",
        patch_file="fix.yaml",
        ran_at=datetime(2025, 1, 15, 10, 30, 0),
        success=True,
        message="patch applied",
    )
    s = r.summary()
    assert "OK" in s
    assert "app.yaml" in s
    assert "fix.yaml" in s
    assert "2025-01-15" in s


def test_summary_failure():
    r = ScheduleResult(
        config_file="app.yaml",
        patch_file="fix.yaml",
        ran_at=datetime(2025, 1, 15, 10, 30, 0),
        success=False,
        message="something broke",
    )
    s = r.summary()
    assert "FAILED" in s
    assert "something broke" in s
