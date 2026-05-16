# Mask Example

The `mask` command lets you display a config file with sensitive values hidden — useful for logging, debugging, or sharing configs safely.

## Basic Usage

```bash
confpatch mask config.yaml --keys password token
```

Given `config.yaml`:
```yaml
host: localhost
port: 5432
password: hunter2
token: abcdef123
```

Output:
```json
{
  "host": "localhost",
  "port": 5432,
  "password": "***",
  "token": "***"
}
```

## Reveal Leading Characters

Use `--reveal N` to show the first N characters:

```bash
confpatch mask config.yaml --keys token --reveal 3
```

Output:
```json
{
  "token": "abc***"
}
```

## Nested Keys

Dot-notation is supported for nested values:

```bash
confpatch mask config.yaml --keys db.password
```

## Summary

Add `--summary` to print a human-readable list of masked keys:

```bash
confpatch mask config.yaml --keys password token --summary
```

```
Masked 2 key(s): password, token
```

## Python API

```python
from confpatch.mask import mask_keys

config = {"password": "secret", "host": "localhost"}
result = mask_keys(config, keys=["password"], reveal_chars=2)
print(result.masked)  # {'password': 'se***', 'host': 'localhost'}
print(result.summary())  # Masked 1 key(s): password
```
