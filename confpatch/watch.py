"""Watch a config file for changes and auto-apply a patch on modification."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    pass


def get_mtime(path: Path) -> float:
    """Return the last modification time of a file."""
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        raise WatchError(f"File not found: {path}")


def watch_file(
    path: Path,
    callback: Callable[[Path], None],
    interval: float = 1.0,
    max_events: Optional[int] = None,
) -> None:
    """
    Poll a file for modifications and invoke callback when changed.

    Args:
        path: Path to the file to watch.
        callback: Function to call with the path when a change is detected.
        interval: Polling interval in seconds.
        max_events: Stop after this many events (None = run forever). Useful for testing.
    """
    path = Path(path)
    last_mtime = get_mtime(path)
    events = 0

    try:
        while True:
            time.sleep(interval)
            try:
                current_mtime = get_mtime(path)
            except WatchError:
                raise

            if current_mtime != last_mtime:
                last_mtime = current_mtime
                callback(path)
                events += 1
                if max_events is not None and events >= max_events:
                    break
    except KeyboardInterrupt:
        pass


def make_patch_callback(
    patch_path: Path,
    on_apply: Optional[Callable[[Path, dict], None]] = None,
) -> Callable[[Path], None]:
    """
    Build a callback that applies a patch file to the changed config.

    Args:
        patch_path: Path to the patch YAML/TOML file.
        on_apply: Optional hook called after a successful apply with (config_path, result).
    """
    from confpatch.patch import load_patch, apply_patch
    from confpatch.loaders import load_config, save_config

    def callback(config_path: Path) -> None:
        config = load_config(config_path)
        patch = load_patch(patch_path)
        updated = apply_patch(config, patch)
        save_config(config_path, updated)
        if on_apply:
            on_apply(config_path, updated)

    return callback
