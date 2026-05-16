# Pipeline Example

The `pipeline` command lets you run a sequence of named steps (patch, transform) against a config file in one shot.

## Steps File Format

Create a JSON file listing your steps:

```json
[
  {
    "name": "bump-version",
    "type": "patch",
    "patch_file": "patches/version.yaml"
  },
  {
    "name": "enable-debug",
    "type": "patch",
    "patch_file": "patches/debug.yaml"
  },
  {
    "name": "coerce-port",
    "type": "transform",
    "patch_file": "patches/port.yaml",
    "transforms": [
      {"path": "app.port", "transform": "int"}
    ]
  }
]
```

## Supported Step Types

| Type        | Description                                      |
|-------------|--------------------------------------------------|
| `patch`     | Apply a YAML/TOML patch file directly            |
| `transform` | Apply a patch file after running value transforms|

## Running a Pipeline

```bash
# Apply all steps and write the result
confpatch pipeline config.yaml steps.json

# Preview without writing
confpatch pipeline config.yaml steps.json --dry-run
```

## Output

```
Pipeline for config.yaml:
  [ok] bump-version: patch applied
  [ok] enable-debug: patch applied
  [ok] coerce-port: transform+patch applied
Result: SUCCESS
```

If a step fails the pipeline stops immediately and reports which step failed:

```
Pipeline for config.yaml:
  [ok] bump-version: patch applied
  [fail] coerce-port: transform 'int' failed on value 'abc'
Result: FAILED
```
