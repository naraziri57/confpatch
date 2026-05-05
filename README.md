# confpatch

Minimal utility to apply structured patches to YAML/TOML config files.

---

## Installation

```bash
pip install confpatch
```

---

## Usage

Apply a patch file to an existing YAML or TOML config:

```bash
confpatch apply config.yaml patch.yaml
```

You can also use it programmatically:

```python
from confpatch import apply_patch

apply_patch("config.yaml", "patch.yaml")
```

**Example `config.yaml`:**

```yaml
server:
  host: localhost
  port: 8080
debug: false
```

**Example `patch.yaml`:**

```yaml
server:
  port: 9090
debug: true
```

**Result:**

```yaml
server:
  host: localhost
  port: 9090
debug: true
```

Patch keys are merged recursively. Existing keys not present in the patch are left untouched. TOML files are supported with the same syntax.

---

## Options

| Flag | Description |
|------|-------------|
| `--in-place` | Overwrite the original file |
| `--output FILE` | Write result to a new file |
| `--format` | Force format: `yaml` or `toml` |

---

## License

MIT © confpatch contributors