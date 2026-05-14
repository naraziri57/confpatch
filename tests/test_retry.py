"""Tests for confpatch.retry."""

from __future__ import annotations

import pytest

from confpatch.retry import retry, RetryError, RetryResult


# ---------------------------------------------------------------------------
# retry()
# ---------------------------------------------------------------------------

def test_retry_succeeds_first_attempt():
    calls = []

    def fn():
        calls.append(1)
        return "ok"

    result = retry(fn, attempts=3, delay=0)
    assert result.success is True
    assert result.value == "ok"
    assert result.attempts == 1
    assert len(calls) == 1


def test_retry_succeeds_on_second_attempt():
    calls = []

    def fn():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("not yet")
        return "done"

    result = retry(fn, attempts=3, delay=0)
    assert result.success is True
    assert result.attempts == 2


def test_retry_exhausts_all_attempts():
    def fn():
        raise RuntimeError("always fails")

    with pytest.raises(RetryError) as exc_info:
        retry(fn, attempts=3, delay=0)

    err = exc_info.value
    assert err.attempts == 3
    assert isinstance(err.last_error, RuntimeError)
    assert "3" in str(err)


def test_retry_only_catches_specified_exceptions():
    def fn():
        raise TypeError("wrong type")

    with pytest.raises(TypeError):
        retry(fn, attempts=3, delay=0, exceptions=(ValueError,))


def test_retry_records_durations():
    result = retry(lambda: 42, attempts=1, delay=0)
    assert len(result.durations) == 1
    assert result.durations[0] >= 0.0


def test_retry_invalid_attempts_raises():
    with pytest.raises(ValueError):
        retry(lambda: None, attempts=0)


# ---------------------------------------------------------------------------
# RetryResult.summary()
# ---------------------------------------------------------------------------

def test_retry_result_summary_success():
    r = RetryResult(success=True, attempts=2, value=None, durations=[0.1, 0.2])
    s = r.summary()
    assert "succeeded" in s
    assert "2 attempt" in s


def test_retry_result_summary_failure():
    r = RetryResult(success=False, attempts=3, value=None, durations=[0.0, 0.0, 0.0])
    s = r.summary()
    assert "failed" in s
    assert "3 attempt" in s


# ---------------------------------------------------------------------------
# RetryError attributes
# ---------------------------------------------------------------------------

def test_retry_error_stores_last_error():
    original = ValueError("boom")

    def fn():
        raise original

    with pytest.raises(RetryError) as exc_info:
        retry(fn, attempts=2, delay=0)

    assert exc_info.value.last_error is original
    assert exc_info.value.attempts == 2
