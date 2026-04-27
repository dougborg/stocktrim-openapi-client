---
name: add-nullable-field
description: >-
  Add a field to NULLABLE_FIELDS in scripts/regenerate_client.py and regenerate
  the client. Use when a TypeError appears in logs or tests because a generated
  model expected a non-null value but the StockTrim API returned null.
allowed-tools: Bash(uv run poe regenerate-client), Bash(uv run poe check), Bash(git status), Bash(git diff *), Read, Edit
---

# /add-nullable-field — Mark a Field Nullable in the Generated Client

Patch `NULLABLE_FIELDS` in the regeneration script, regenerate, validate, and document.

## PURPOSE

Make a generated model field nullable so the client stops crashing on null API responses — without adding `# type: ignore`.

## CRITICAL

- **Never use `# type: ignore` to silence the error** — that's a forbidden shortcut per CLAUDE.md. Add the field to `NULLABLE_FIELDS` and regenerate.
- **Never edit `stocktrim_public_api_client/generated/` directly** — changes are lost on regeneration.
- **The fix must be reproducible from the spec** — anyone running `uv run poe regenerate-client` must get the same result.

## ASSUMES

- You have an actual error message identifying the schema and field (e.g., `PurchaseOrderResponseDto.orderDate` returns null but spec marks it required).
- `scripts/regenerate_client.py` exists and contains a `NULLABLE_FIELDS` dict.

## STANDARD PATH

### 1. Identify schema + field

From the error message, extract:

- Schema name (e.g., `PurchaseOrderResponseDto`)
- Field name (e.g., `orderDate`)
- Field type (date-time, string, object, etc. — useful for the comment)

### 2. Add to NULLABLE_FIELDS

Open `scripts/regenerate_client.py`, find `NULLABLE_FIELDS` (around line 168), and add:

```python
NULLABLE_FIELDS = {
    "PurchaseOrderResponseDto": [
        # ...existing fields...
        "newField",  # type — short note on observed null behavior
    ],
    # Add new schema if needed:
    "NewSchemaName": [
        "fieldName",  # type
    ],
}
```

Use the same comment style as existing entries. Mark with `⚠️ CRITICAL` if null actually crashes (not just wrong types).

### 3. Regenerate

```bash
uv run poe regenerate-client
```

### 4. Validate

```bash
uv run poe check
```

ALL must pass. If a different field is now broken, repeat from step 1 — don't bail with `# type: ignore`.

### 5. Confirm the diff is bounded

```bash
git diff --stat
```

You should see:

- `scripts/regenerate_client.py` (1 small change)
- `stocktrim_public_api_client/generated/models/<schema>.py` (the field becomes `Optional`)
- Possibly `client_types.py` if reexports change

If the diff is much bigger, regeneration picked up an unrelated upstream change. Stash, run regeneration on a clean baseline, then re-apply your `NULLABLE_FIELDS` change.

### 6. Document evidence (optional)

If `docs/contributing/api-feedback.md` exists, append a row noting the schema + field + observed behavior. This is the canonical record for "spec says required, API returns null."

## EDGE CASES

- [Field is in a deeply nested array item] — `NULLABLE_FIELDS` works at the top level of a schema. For nested types, check whether the nested schema is itself a top-level component (it usually is) and add it there.
- [Field is required in some endpoints but not others] — `NULLABLE_FIELDS` marks the schema field nullable everywhere it's used. Acceptable trade-off; document in the comment.

## RELATED

- `/regenerate-client` — Full regeneration workflow
- `domain-advisor` agent — Explains why fields are nullable
