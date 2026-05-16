# Copy Key Example

The `copy` command lets you duplicate keys within a config file, including nested paths using dot notation.

## Basic Usage

Copy a top-level key:

```bash
confpatch copy config.yaml database.host backup.host
```

This will read `database.host` and write its value to `backup.host`, creating intermediate keys if needed.

## Multiple Pairs

You can copy several keys at once:

```bash
confpatch copy config.yaml database.host:backup.host database.port:backup.port
```

## Overwriting Existing Keys

By default, if the destination key already exists it is **skipped**. Use `--overwrite` to replace it:

```bash
confpatch copy config.yaml database.host:backup.host --overwrite
```

## Dry Run

Preview what would be copied without modifying the file:

```bash
confpatch copy config.yaml database.host:backup.host --dry-run
```

Example output:

```
[dry-run] Copied 1 key(s).
  database.host -> backup.host
```

## Example Config

Before:

```yaml
database:
  host: localhost
  port: 5432
```

After `confpatch copy config.yaml database.host:backup.host database.port:backup.port`:

```yaml
database:
  host: localhost
  port: 5432
backup:
  host: localhost
  port: 5432
```

## Notes

- Source keys must exist; a missing source is an error.
- Destination intermediate dicts are created automatically.
- The original config is never mutated in memory; a deep copy is used.
