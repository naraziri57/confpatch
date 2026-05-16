# Schedule Example

The `schedule` feature lets you apply a patch to a config file after a delay or at a specific time.

## Apply after a delay

```bash
confpatch schedule config.yaml patch.yaml --after 30
```

This waits 30 seconds, then applies `patch.yaml` to `config.yaml`.

## Apply at a specific time

```bash
confpatch schedule config.yaml patch.yaml --at 2025-06-01T03:00:00
```

This blocks until the given ISO datetime, then applies the patch.

## Programmatic usage

```python
from datetime import datetime, timedelta
from confpatch.schedule import run_after, run_at
from confpatch.loaders import load_config, save_config
from confpatch.patch import apply_patch, load_patch

def my_apply(config_file, patch_file):
    config = load_config(config_file, fmt="yaml")
    patch = load_patch(patch_file)
    updated = apply_patch(config, patch)
    save_config(updated, config_file, fmt="yaml")

# Run after 10 seconds
result = run_after(10, "config.yaml", "patch.yaml", my_apply)
print(result.summary())

# Run at a specific time
target = datetime(2025, 6, 1, 3, 0, 0)
result = run_at(target, "config.yaml", "patch.yaml", my_apply)
print(result.summary())
```

## ScheduleResult

Both `run_after` and `run_at` return a `ScheduleResult`:

| Field | Description |
|-------|-------------|
| `config_file` | Path to the config that was patched |
| `patch_file` | Path to the patch that was applied |
| `ran_at` | `datetime` when the patch ran |
| `success` | `True` if patch succeeded |
| `message` | Short status message or error |

```python
if result.success:
    print("Patch applied successfully!")
else:
    print(f"Patch failed: {result.message}")
```

## Error handling

`ScheduleError` is raised if the target time is in the past or the delay is negative:

```python
from confpatch.schedule import ScheduleError

try:
    run_after(-5, "config.yaml", "patch.yaml", my_apply)
except ScheduleError as e:
    print(f"Invalid schedule: {e}")
```
