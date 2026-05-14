# Secret Redaction Example

`confpatch` can detect and mask sensitive values in patch files before they are
displayed or logged, helping you avoid accidentally leaking credentials.

## Sensitive key patterns (built-in)

The following key patterns are considered sensitive by default:

- `password`
- `secret`
- `token`
- `api_key` / `api-key`
- `private_key` / `private-key`

Matching is **case-insensitive** and uses substring search.

## Preview a patch with secrets masked

```bash
confpatch redact patch.yaml
```

Example output:

```
Redacted patch preview:
  username: admin
  password: ***
  api_key: ***

Redacted 2 sensitive key(s): password, api_key
```

## List sensitive keys in a patch

```bash
confpatch list-sensitive patch.yaml
```

Example output:

```
Sensitive keys detected:
  - password
  - api_key
```

## Using redaction in Python

```python
from confpatch.secret import redact_patch

patch = {
    "username": "admin",
    "password": "hunter2",
    "db": {
        "host": "localhost",
        "password": "dbpass",
    },
}

redacted, result = redact_patch(patch)
print(redacted)
# {'username': 'admin', 'password': '***', 'db': {'host': 'localhost', 'password': '***'}}
print(result.summary())
# Redacted 2 sensitive key(s): password, db.password
```

## Custom patterns

```python
import re
from confpatch.secret import redact_patch

custom_patterns = [re.compile(r"pin", re.IGNORECASE)]
redacted, result = redact_patch({"pin": "9999", "name": "alice"}, patterns=custom_patterns)
# pin is masked, name is not
```
