"""Pre/post apply hooks for confpatch."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class HookError(Exception):
    """Raised when a hook fails."""


@dataclass
class HookResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass
class HookConfig:
    pre: List[str] = field(default_factory=list)
    post: List[str] = field(default_factory=list)


def _run_command(command: str, cwd: Optional[Path] = None) -> HookResult:
    """Run a shell command and return the result."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
        return HookResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
        )
    except Exception as exc:
        raise HookError(f"Failed to run hook command '{command}': {exc}") from exc


def run_hooks(commands: List[str], cwd: Optional[Path] = None) -> List[HookResult]:
    """Run a list of hook commands sequentially. Raises HookError on first failure."""
    results: List[HookResult] = []
    for cmd in commands:
        result = _run_command(cmd, cwd=cwd)
        results.append(result)
        if not result.ok:
            raise HookError(
                f"Hook command failed (exit {result.returncode}): {cmd}\n"
                f"stderr: {result.stderr}"
            )
    return results


def load_hooks(config: dict) -> HookConfig:
    """Load hook configuration from a config dict (e.g. from patch metadata)."""
    hooks_data = config.get("hooks", {})
    if not isinstance(hooks_data, dict):
        raise HookError("'hooks' must be a mapping with 'pre' and/or 'post' keys")
    pre = hooks_data.get("pre", [])
    post = hooks_data.get("post", [])
    if not isinstance(pre, list) or not isinstance(post, list):
        raise HookError("'hooks.pre' and 'hooks.post' must be lists of commands")
    return HookConfig(pre=pre, post=post)
