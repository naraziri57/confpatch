"""Tests for confpatch.lint module."""

from __future__ import annotations

import pytest

from confpatch.lint import LintResult, LintWarning, lint_patch


def test_lint_valid_patch():
    result = lint_patch({"database.host": "localhost", "app.debug": False})
    assert result.ok
    assert result.warnings == []
    assert result.errors == []


def test_lint_not_a_dict():
    result = lint_patch(["not", "a", "dict"])
    assert not result.ok
    assert any("must be a dict" in e.message for e in result.errors)


def test_lint_empty_patch():
    result = lint_patch({})
    assert result.ok  # empty is a warning, not an error
    assert any("empty" in w.message for w in result.warnings)


def test_lint_null_value_warns():
    result = lint_patch({"some.key": None})
    assert result.ok
    assert any("null" in w.message.lower() for w in result.warnings)


def test_lint_env_var_like_value_warns():
    result = lint_patch({"api.token": "$MY_SECRET"})
    assert result.ok
    assert any("unresolved env" in w.message for w in result.warnings)


def test_lint_key_with_whitespace_warns():
    result = lint_patch({" padded.key ": "value"})
    assert result.ok
    assert any("whitespace" in w.message for w in result.warnings)


def test_lint_key_with_spaces_no_dots_warns():
    result = lint_patch({"some key": "value"})
    assert result.ok
    assert any("dot notation" in w.message for w in result.warnings)


def test_lint_result_summary_no_issues():
    result = LintResult()
    assert result.summary() == "No lint issues found."


def test_lint_result_summary_with_issues():
    result = LintResult(
        warnings=[LintWarning("x", "watch out")],
        errors=[LintWarning("y", "bad thing")],
    )
    summary = result.summary()
    assert "WARN" in summary
    assert "ERROR" in summary
    assert "watch out" in summary
    assert "bad thing" in summary


def test_lint_result_ok_with_warnings():
    result = LintResult(warnings=[LintWarning("k", "minor")])
    assert result.ok


def test_lint_result_not_ok_with_errors():
    result = LintResult(errors=[LintWarning("k", "bad")])
    assert not result.ok
