# Clamp Example

The `clamp` feature allows you to enforce numeric boundaries on values in your config files.

## Use Case

You have a config with numeric values that must stay within a safe operating range.

## Example Config (`config.yaml`)

```yaml
server:
  timeout: 9999
  retries: 10
workers: 512
label: production
```

## CLI Usage

### Clamp all numeric values to a max of 100

```bash
confpatch clamp config.yaml --max 100
```

Output:
```
Clamped 3 value(s):
  server.timeout: 9999 -> 100
  server.retries: 10 -> 10
  workers: 512 -> 100
Saved: config.yaml
```

### Clamp with both min and max

```bash
confpatch clamp config.yaml --min 1 --max 100
```

### Clamp only specific keys

```bash
confpatch clamp config.yaml --max 100 --keys server.timeout workers
```

### Preview without writing

```bash
confpatch clamp config.yaml --max 100 --dry-run
```

## Python API

```python
from confpatch.clamp import clamp_config

config = {"timeout": 9999, "retries": 3, "label": "prod"}
result = clamp_config(config, min_val=1, max_val=100)

print(result.summary())
# Clamped 1 value(s):
#   timeout: 9999 -> 100

print(result.clamped)
# {'timeout': 100, 'retries': 3, 'label': 'prod'}
```

## Notes

- Non-numeric values (strings, lists, etc.) are always passed through unchanged.
- Integer types stay integers; floats stay floats after clamping.
- Use `--keys` to restrict clamping to specific dot-notation paths.
