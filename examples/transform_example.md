# Transform Example

The `transform` feature lets you coerce or reformat patch values before they are applied to a config file.

## Available Transforms

| Name    | Description                                |
|---------|--------------------------------------------|
| `int`   | Convert value to integer                   |
| `float` | Convert value to float                     |
| `str`   | Convert value to string                    |
| `bool`  | Coerce to bool (`true/yes/1` → `True`)     |
| `upper` | Convert string to uppercase                |
| `lower` | Convert string to lowercase                |
| `strip` | Strip leading/trailing whitespace          |
| `null`  | Set value to `null` / `None`               |

## Python API

```python
from confpatch.transform import apply_transform, apply_transforms_to_patch

# Single value
apply_transform("8080", "int")   # → 8080
apply_transform("Debug", "lower") # → "debug"

# Whole patch dict
patch = {"port": "8080", "server": {"host": "  localhost  "}}
transforms = {"port": "int", "server.host": "strip"}
result = apply_transforms_to_patch(patch, transforms)
# result → {"port": 8080, "server": {"host": "localhost"}}
```

## CLI

```bash
# Apply a transform to a single value
confpatch transform 8080 int
# → 8080

confpatch transform "  hello  " strip
# → hello

# List all available transforms
confpatch list-transforms
```
