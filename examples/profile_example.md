# Patch Profiles Example

Profiles let you save a named patch and re-apply it to any config file later.

## Save a profile

```bash
# patch.json contains the patch dict, e.g. {"log_level": "debug", "workers": 4}
confpatch profile-save dev patch.json --description "Dev overrides" --tags dev local
```

## List profiles

```bash
confpatch profile-list
# dev                   tags=[dev, local]  Dev overrides
```

## Apply a profile

```bash
confpatch profile-apply dev config.yaml
# Applied profile 'dev' to config.yaml

# Dry run — preview without writing
confpatch profile-apply dev config.yaml --dry-run
```

## Delete a profile

```bash
confpatch profile-delete dev
# Profile 'dev' deleted.
```

## Where profiles are stored

By default profiles are stored in `.confpatch/profiles.json` in the current
directory. Override with `--store /path/to/dir`.

## Profile format (profiles.json)

```json
[
  {
    "name": "dev",
    "patch": {"log_level": "debug", "workers": 4},
    "description": "Dev overrides",
    "tags": ["dev", "local"]
  }
]
```
