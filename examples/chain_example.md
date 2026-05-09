# Patch Chaining Example

Apply multiple patch files to a config in sequence using `confpatch chain`.

## Setup

```yaml
# config.yaml
name: myapp
version: 1
debug: false
database:
  host: localhost
  port: 5432
```

```yaml
# patch_version.yaml
version: 2
```

```yaml
# patch_debug.yaml
debug: true
```

```yaml
# patch_db.yaml
database.host: db.prod.internal
```

## Apply the chain

```bash
confpatch chain config.yaml patch_version.yaml patch_debug.yaml patch_db.yaml
```

Output:
```
Chain on 'config.yaml': 3 applied, 0 failed
  [ok]   patch_version.yaml
  [ok]   patch_debug.yaml
  [ok]   patch_db.yaml
```

## Keep going on failure

By default the chain stops at the first failed patch. Use `--keep-going` to
continue applying remaining patches even if one fails:

```bash
confpatch chain config.yaml bad.yaml patch_debug.yaml --keep-going
```

## Dry run

Preview all changes without writing anything to disk:

```bash
confpatch chain config.yaml patch_version.yaml patch_db.yaml --dry-run
```

## Python API

```python
from confpatch.chain import apply_chain

result = apply_chain(
    config_path="config.yaml",
    patch_paths=["patch_version.yaml", "patch_debug.yaml"],
    stop_on_error=True,
    dry_run=False,
)

print(result.summary())
for p in result.patches_applied:
    print(f"  applied: {p}")
```
