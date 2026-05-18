# collect example

The `collect` command extracts specific keys from a config file and prints them.

## Basic usage

```bash
confpatch collect config.yaml host port
```

Output:
```
host: localhost
port: 8080
```

## Dot notation

Use dot notation to reach nested keys:

```bash
confpatch collect config.yaml database.host database.port
```

## JSON output

Add `--json` to get machine-readable output:

```bash
confpatch collect config.yaml database.host --json
```

Output:
```json
{
  "database.host": "localhost"
}
```

## Skipping missing keys

By default, missing keys raise an error. Use `--skip-missing` to ignore them:

```bash
confpatch collect config.yaml host missing_key --skip-missing
```

Missing keys are reported to stderr but the command still succeeds.

## Python API

```python
from confpatch.collect import collect_keys

config = {"db": {"host": "localhost", "port": 5432}, "debug": True}

result = collect_keys(config, ["db.host", "debug"])
print(result.collected)   # {"db.host": "localhost", "debug": True}
print(result.summary())   # Collected 2 key(s)
```
