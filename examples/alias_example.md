# Alias Example

Aliases let you assign short names to patch file paths, so you don't have to
remember or retype long paths repeatedly.

## Adding an alias

```bash
confpatch alias-add config.yaml prod patches/production.yaml
# Alias 'prod' -> 'patches/production.yaml' saved.
```

## Listing aliases

```bash
confpatch alias-list config.yaml
#   prod                 -> patches/production.yaml
#   staging              -> patches/staging.yaml
```

## Resolving an alias

Resolve prints the real path, useful for scripting:

```bash
confpatch alias-resolve config.yaml prod
# patches/production.yaml

# Use in a shell pipeline:
confpatch apply config.yaml $(confpatch alias-resolve config.yaml prod)
```

## Removing an alias

```bash
confpatch alias-remove config.yaml prod
# Alias 'prod' removed.
```

## Programmatic usage

```python
from pathlib import Path
from confpatch.alias import add_alias, resolve_alias, list_aliases

config = Path("config.yaml")

add_alias(config, "prod", "patches/production.yaml")
add_alias(config, "dev",  "patches/dev.yaml")

for name, path in list_aliases(config):
    print(f"{name} => {path}")

patch_path = resolve_alias(config, "prod")
print(patch_path)  # patches/production.yaml
```

## Storage

Aliases are stored in a hidden JSON file next to your config:

```
config.yaml
.config_aliases.json   <- auto-created
```

This file is human-readable and can be committed to version control.
