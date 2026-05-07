"""Lint rules for patch files — catch common mistakes before applying."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class LintError(Exception):
    pass


@dataclass
class LintWarning:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


@dataclass
class LintResult:
    warnings: list[LintWarning] = field(default_factory=list)
    errors: list[LintWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        for w in self.warnings:
            lines.append(f"WARN  {w}")
        for e in self.errors:
            lines.append(f"ERROR {e}")
        if not lines:
            return "No lint issues found."
        return "\n".join(lines)


def _check_key(key: str, value: Any, result: LintResult) -> None:
    if not isinstance(key, str):
        result.errors.append(LintWarning(str(key), "Key must be a string"))
        return

    if key != key.strip():
        result.warnings.append(LintWarning(key, "Key has leading/trailing whitespace"))

    if " " in key and "." not in key:
        result.warnings.append(LintWarning(key, "Key contains spaces — did you mean dot notation?"))

    if value is None:
        result.warnings.append(LintWarning(key, "Value is null — this will set the key to None"))

    if isinstance(value, str) and value.startswith("$"):
        result.warnings.append(LintWarning(key, "Value looks like an unresolved env variable"))


def lint_patch(patch: Any) -> LintResult:
    """Run lint checks on a patch dict and return a LintResult."""
    result = LintResult()

    if not isinstance(patch, dict):
        result.errors.append(LintWarning("<root>", "Patch must be a dict"))
        return result

    if len(patch) == 0:
        result.warnings.append(LintWarning("<root>", "Patch is empty"))
        return result

    for key, value in patch.items():
        _check_key(key, value, result)

    return result
