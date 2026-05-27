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

Run the OpenAPI regeneration pipeline, validate, and commit the result on a feature
branch.

## PURPOSE

Replace the generated client with a fresh build from the live spec, with all
post-processing applied.

## CRITICAL

- **ALWAYS use the full pipeline (`uv run poe regenerate-client`).** Surgical regens —
  manually running `openapi-python-client generate` against the cached spec and copying
  1–2 files into `generated/` — are an **ANTI-PATTERN**. They bypass the live spec
  download, leave the rest of `generated/` frozen against the older generator, and
  accumulate drift bugs (stale field types, bare-except patterns, missing nullable
  markers). If you need to regenerate ANYTHING, regenerate EVERYTHING.
- **Default: absorb upstream drift in the same PR as additional commits.** Keep the
  immediate-fix commit focused, then add follow-up commits adapting
  helpers/services/tests for whatever the regen brought in. Do not stash or reset to
  keep the diff small.
- **Deferral protocol (only when you absolutely cannot ship the regen in the same PR):**
  ALL of the following are mandatory:
  1. File a `tech-debt` tracking issue noting the regen is owed and why it was deferred.
  1. Open the regen PR as the very next piece of work — no unrelated tasks first.
  1. Reference the tracking issue from the deferring PR's description.
- **Never hand-edit `stocktrim_public_api_client/generated/` or `client_types.py`** —
  both are wholly replaced by this skill. Edits are silently lost.
- **All type/null fixes go in `scripts/regenerate_client.py`** — never add
  `# type: ignore` to generated code; add the field to `NULLABLE_FIELDS` instead.
- **Must be on a feature branch** — never regenerate directly on `main`.
- **CLAUDE.md zero-tolerance applies** — `uv run poe check` must be green before
  committing.

## ASSUMES

- You're in a git repository on a feature branch (or willing to create one).
- The live StockTrim spec at `https://api.stocktrim.com/swagger/v1/swagger.yaml` is
  reachable.
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
1. Patches auth (header params → securitySchemes)
1. Validates with `openapi-spec-validator` and Redocly
1. Generates the client via `openapi-python-client`
1. Renames `types.py` → `client_types.py` and rewrites imports
1. Modernizes `Union[X, Y]` → `X | Y`
1. Fixes RST docstrings
1. Applies `NULLABLE_FIELDS` overrides
1. Runs `ruff --fix`

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

- **Type error on null field?** → Add to `NULLABLE_FIELDS` in
  `scripts/regenerate_client.py`, re-run from Step 2. Never add `# type: ignore`.
- **Helper method broken by renamed model?** → Update the helper. Helpers wrap
  generated/, so they need to track renames.
- **MCP tool broken?** → Update the corresponding service in
  `stocktrim_mcp_server/src/.../services/`.

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

Use `feat(client):` scope for client release; add `chore(mcp):` companion commit if MCP
services were updated.

## EDGE CASES

- [Spec download fails] — Check `SPEC_URL` in `scripts/regenerate_client.py`. Network
  issue? Retry. Permanent? Open an issue.
- [Generation breaks for an unrelated schema] — Read DETAIL: Quarantining a Schema
- [Helper or test fails after regen] — Update the helper/test. Generated code is the
  source of truth; downstream code adapts.

## DETAIL: Quarantining a Schema

If a schema generates uncompilable code (rare), patch it in
`scripts/regenerate_client.py` before the generation step rather than editing the
generated output.

## RELATED

- `/add-nullable-field` — When the only fix needed is a new `NULLABLE_FIELDS` entry
- `domain-advisor` agent — Explains the spec-vs-real-API divergences
- CLAUDE.md "DO NOT EDIT generated/" rule
