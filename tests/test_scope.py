"""Tests for confpatch.scope."""

import pytest

from confpatch.scope import (
    ScopeError,
    apply_scoped_patch,
    extract_scope,
    _get_subtree,
    _set_subtree,
)


BASE_CONFIG = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "tls": {"enabled": False, "cert": "/etc/cert.pem"},
    },
    "database": {"url": "sqlite:///db.sqlite3"},
}


def test_get_subtree_top_level():
    result = _get_subtree(BASE_CONFIG, "server")
    assert result["host"] == "localhost"


def test_get_subtree_nested():
    result = _get_subtree(BASE_CONFIG, "server.tls")
    assert result["enabled"] is False


def test_get_subtree_missing_key_raises():
    with pytest.raises(ScopeError, match="not found"):
        _get_subtree(BASE_CONFIG, "server.missing")


def test_get_subtree_non_dict_raises():
    with pytest.raises(ScopeError, match="not a dict"):
        _get_subtree(BASE_CONFIG, "server.host")


def test_set_subtree_returns_new_config():
    new_tree = {"host": "0.0.0.0", "port": 443}
    result = _set_subtree(BASE_CONFIG, "server", new_tree)
    assert result["server"]["host"] == "0.0.0.0"
    # original untouched
    assert BASE_CONFIG["server"]["host"] == "localhost"


def test_set_subtree_nested():
    new_tls = {"enabled": True, "cert": "/new/cert.pem"}
    result = _set_subtree(BASE_CONFIG, "server.tls", new_tls)
    assert result["server"]["tls"]["enabled"] is True
    assert BASE_CONFIG["server"]["tls"]["enabled"] is False


def test_apply_scoped_patch_modifies_subtree():
    patch = {"port": 9090}
    result = apply_scoped_patch(BASE_CONFIG, patch, "server")
    assert result["server"]["port"] == 9090
    assert result["server"]["host"] == "localhost"


def test_apply_scoped_patch_does_not_mutate_original():
    patch = {"port": 1234}
    apply_scoped_patch(BASE_CONFIG, patch, "server")
    assert BASE_CONFIG["server"]["port"] == 8080


def test_apply_scoped_patch_leaves_other_keys_intact():
    patch = {"url": "postgres://localhost/prod"}
    result = apply_scoped_patch(BASE_CONFIG, patch, "database")
    assert result["server"]["host"] == "localhost"
    assert result["database"]["url"] == "postgres://localhost/prod"


def test_apply_scoped_patch_invalid_scope_raises():
    with pytest.raises(ScopeError):
        apply_scoped_patch(BASE_CONFIG, {"x": 1}, "nonexistent")


def test_extract_scope_returns_copy():
    result = extract_scope(BASE_CONFIG, "server")
    assert result["host"] == "localhost"
    result["host"] = "changed"
    assert BASE_CONFIG["server"]["host"] == "localhost"


def test_extract_scope_nested():
    result = extract_scope(BASE_CONFIG, "server.tls")
    assert result == {"enabled": False, "cert": "/etc/cert.pem"}
