"""Tests for confpatch.secret."""

import pytest
from confpatch.secret import (
    MASK,
    RedactResult,
    SecretError,
    _is_sensitive,
    redact_patch,
    redact_value,
    DEFAULT_PATTERNS,
)


def test_is_sensitive_password():
    assert _is_sensitive("password", DEFAULT_PATTERNS) is True


def test_is_sensitive_token():
    assert _is_sensitive("auth_token", DEFAULT_PATTERNS) is True


def test_is_sensitive_api_key():
    assert _is_sensitive("api_key", DEFAULT_PATTERNS) is True


def test_is_sensitive_non_sensitive():
    assert _is_sensitive("username", DEFAULT_PATTERNS) is False


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("PASSWORD", DEFAULT_PATTERNS) is True


def test_redact_value_scalar():
    assert redact_value("mysecret") == MASK


def test_redact_value_dict_passthrough():
    d = {"a": 1}
    assert redact_value(d) is d


def test_redact_value_list_passthrough():
    lst = [1, 2]
    assert redact_value(lst) is lst


def test_redact_patch_masks_password():
    patch = {"password": "hunter2", "username": "admin"}
    out, result = redact_patch(patch)
    assert out["password"] == MASK
    assert out["username"] == "admin"


def test_redact_patch_does_not_mutate_original():
    patch = {"password": "secret123"}
    original = dict(patch)
    redact_patch(patch)
    assert patch == original


def test_redact_patch_nested():
    patch = {"db": {"password": "pass", "host": "localhost"}}
    out, result = redact_patch(patch)
    assert out["db"]["password"] == MASK
    assert out["db"]["host"] == "localhost"
    assert "db.password" in result.redacted_keys


def test_redact_patch_no_sensitive_keys():
    patch = {"host": "localhost", "port": 5432}
    out, result = redact_patch(patch)
    assert out == patch
    assert result.redacted_count == 0


def test_redact_patch_invalid_input():
    with pytest.raises(SecretError):
        redact_patch(["not", "a", "dict"])


def test_redact_result_summary_with_keys():
    r = RedactResult(redacted_keys=["password", "token"])
    summary = r.summary()
    assert "2" in summary
    assert "password" in summary


def test_redact_result_summary_empty():
    r = RedactResult()
    assert "No sensitive" in r.summary()


def test_redact_patch_custom_patterns():
    import re
    custom = [re.compile(r"pin", re.IGNORECASE)]
    patch = {"pin": "1234", "password": "abc"}
    out, result = redact_patch(patch, patterns=custom)
    assert out["pin"] == MASK
    assert out["password"] == "abc"  # not matched by custom pattern
