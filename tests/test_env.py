"""Tests for confpatch.env — environment variable injection."""

import pytest
from confpatch.env import EnvError, inject_env, inject_patch_env, _inject_string


def test_inject_string_simple(monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    result = _inject_string("host=${APP_HOST}")
    assert result == "host=localhost"


def test_inject_string_multiple_vars(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    result = _inject_string("${HOST}:${PORT}")
    assert result == "127.0.0.1:8080"


def test_inject_string_missing_var_strict_raises(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(EnvError, match="MISSING_VAR"):
        _inject_string("${MISSING_VAR}", strict=True)


def test_inject_string_missing_var_non_strict(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    result = _inject_string("${MISSING_VAR}", strict=False)
    assert result == "${MISSING_VAR}"


def test_inject_env_non_string_passthrough():
    assert inject_env(42) == 42
    assert inject_env(3.14) == 3.14
    assert inject_env(True) is True
    assert inject_env(None) is None


def test_inject_env_nested_dict(monkeypatch):
    monkeypatch.setenv("DB_PASS", "secret")
    value = {"password": "${DB_PASS}", "port": 5432}
    result = inject_env(value)
    assert result == {"password": "secret", "port": 5432}


def test_inject_env_list(monkeypatch):
    monkeypatch.setenv("ITEM", "resolved")
    result = inject_env(["${ITEM}", "static", 99])
    assert result == ["resolved", "static", 99]


def test_inject_env_deeply_nested(monkeypatch):
    monkeypatch.setenv("SECRET", "topsecret")
    value = {"level1": {"level2": {"key": "${SECRET}"}}}
    result = inject_env(value)
    assert result["level1"]["level2"]["key"] == "topsecret"


def test_inject_patch_env_basic(monkeypatch):
    monkeypatch.setenv("API_KEY", "abc123")
    patch = {"service.api_key": "${API_KEY}", "service.timeout": 30}
    result = inject_patch_env(patch)
    assert result["service.api_key"] == "abc123"
    assert result["service.timeout"] == 30


def test_inject_patch_env_non_dict_raises():
    with pytest.raises(EnvError, match="dictionary"):
        inject_patch_env(["not", "a", "dict"])


def test_inject_patch_env_missing_var_strict(monkeypatch):
    monkeypatch.delenv("UNDEFINED", raising=False)
    with pytest.raises(EnvError):
        inject_patch_env({"key": "${UNDEFINED}"}, strict=True)


def test_inject_patch_env_missing_var_non_strict(monkeypatch):
    monkeypatch.delenv("UNDEFINED", raising=False)
    result = inject_patch_env({"key": "${UNDEFINED}"}, strict=False)
    assert result["key"] == "${UNDEFINED}"
