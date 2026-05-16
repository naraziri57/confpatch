# Reorder Example

The `reorder` command lets you sort the keys in a YAML or TOML config file into a specific order — useful for standardizing config layouts across environments.

## Basic usage

Given `config.yaml`:

```yaml
port: 8080
host: localhost
debug: true
```

Run:

```bash
confpatch reorder config.yaml host port debug
```

Result:

```yaml
host: localhost
port: 8080
debug: true
```

## Scoped reorder

Reorder keys inside a nested section using `--scope`:

```bash
confpatch reorder config.yaml user pass host --scope database
```

Only the keys under `database` are reordered; the rest of the file is unchanged.

## Dry run

Preview what would change without writing:

```bash
confpatch reorder config.yaml host port --dry-run
```

## Notes

- Keys listed in the order that don't exist in the config are silently skipped.
- Keys present in the config but not listed in the order are appended after the ordered keys in their original relative order.
- Works with both YAML and TOML files.
