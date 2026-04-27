---
name: regenerate-client
description: >-
  Regenerate the StockTrim OpenAPI client from the live spec, run quality
  checks, and commit the result. Use when the StockTrim API spec changes,
  a new endpoint is added, or NULLABLE_FIELDS in scripts/regenerate_client.py
  is updated.
allowed-tools: Bash(uv run poe regenerate-client), Bash(uv run poe check), Bash(uv run poe validate-openapi*), Bash(git status), Bash(git diff *), Bash(git add *), Bash(git commit *), Bash(git checkout *), Bash(git branch *), Read
---

# /regenerate-client — Regenerate the StockTrim API Client

Run the OpenAPI regeneration pipeline, validate, and commit the result on a feature branch.

## PURPOSE

Replace the generated client with a fresh build from the live spec, with all post-processing applied.

## CRITICAL

- **Never hand-edit `stocktrim_public_api_client/generated/` or `client_types.py`** — both are wholly replaced by this skill. Edits are silently lost.
- **All type/null fixes go in `scripts/regenerate_client.py`** — never add `# type: ignore` to generated code; add the field to `NULLABLE_FIELDS` instead.
- **Must be on a feature branch** — never regenerate directly on `main`.
- **CLAUDE.md zero-tolerance applies** — `uv run poe check` must be green before committing.

## ASSUMES

- You're in a git repository on a feature branch (or willing to create one).
- The live StockTrim spec at `https://api.stocktrim.com/swagger/v1/swagger.yaml` is reachable.
- `uv` and project deps are installed (`uv sync`).

## STANDARD PATH

### 1. Pre-flight

```bash
git status                     # Working tree should be clean
git branch --show-current      # Confirm not on main
```

If on `main`, switch: `git checkout -b chore/regenerate-client-$(date +%Y%m%d)`.

### 2. Run the regeneration

```bash
uv run poe regenerate-client
```

This invokes `scripts/regenerate_client.py` which:

1. Downloads the spec
2. Patches auth (header params → securitySchemes)
3. Validates with `openapi-spec-validator` and Redocly
4. Generates the client via `openapi-python-client`
5. Renames `types.py` → `client_types.py` and rewrites imports
6. Modernizes `Union[X, Y]` → `X | Y`
7. Fixes RST docstrings
8. Applies `NULLABLE_FIELDS` overrides
9. Runs `ruff --fix`

### 3. Inspect the diff

```bash
git status
git diff --stat stocktrim_public_api_client/generated/ stocktrim_public_api_client/client_types.py
```

Review for unexpected churn (renamed models, removed endpoints).

### 4. Validate

```bash
uv run poe check
```

ALL must pass. If failures appear:

- **Type error on null field?** → Add to `NULLABLE_FIELDS` in `scripts/regenerate_client.py`, re-run from Step 2. Never add `# type: ignore`.
- **Helper method broken by renamed model?** → Update the helper. Helpers wrap generated/, so they need to track renames.
- **MCP tool broken?** → Update the corresponding service in `stocktrim_mcp_server/src/.../services/`.

### 5. Commit on feature branch

```bash
git add stocktrim-openapi.yaml stocktrim_public_api_client/ scripts/regenerate_client.py
git commit -m "$(cat <<'EOF'
feat(client): regenerate from latest OpenAPI spec

- Pull latest stocktrim-openapi.yaml
- Apply NULLABLE_FIELDS overrides
- Run ruff auto-fixes

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

Use `feat(client):` scope for client release; add `chore(mcp):` companion commit if MCP services were updated.

## EDGE CASES

- [Spec download fails] — Check `SPEC_URL` in `scripts/regenerate_client.py`. Network issue? Retry. Permanent? Open an issue.
- [Generation breaks for an unrelated schema] — Read DETAIL: Quarantining a Schema
- [Helper or test fails after regen] — Update the helper/test. Generated code is the source of truth; downstream code adapts.

## DETAIL: Quarantining a Schema

If a schema generates uncompilable code (rare), patch it in `scripts/regenerate_client.py` before the generation step rather than editing the generated output.

## RELATED

- `/add-nullable-field` — When the only fix needed is a new `NULLABLE_FIELDS` entry
- `domain-advisor` agent — Explains the spec-vs-real-API divergences
- CLAUDE.md "DO NOT EDIT generated/" rule
