# Index Feature Example

The `index` module lets you build a searchable index of all config keys across multiple files.

## Build an index

```bash
confpatch index-build config.yaml settings.toml --output .confpatch_index.json
# [ok] indexed 14 keys from 2 file(s) -> .confpatch_index.json
```

## Search keys

```bash
confpatch index-search host
#   config.yaml  database.host = 'localhost'
```

## List all keys

```bash
confpatch index-list
#   config.yaml  database.host = 'localhost'
#   config.yaml  database.port = 5432
#   config.yaml  app.debug = True
#   settings.toml  server.timeout = 30
```

## Python API

```python
from confpatch.index import build_index, search_index, save_index, load_index

# Build from files
entries = build_index(["config.yaml", "settings.toml"])

# Search
results = search_index(entries, "database")
for r in results:
    print(r.file, r.key, r.value)

# Persist and reload
save_index(entries, ".confpatch_index.json")
loaded = load_index(".confpatch_index.json")
```

## Use cases

- Quickly find which file contains a given key
- Audit all config values across a large project
- Detect duplicate keys defined in multiple files
