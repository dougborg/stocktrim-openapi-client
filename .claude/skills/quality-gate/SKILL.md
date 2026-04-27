---
name: quality-gate
description: >-
  Run the full CLAUDE.md zero-tolerance quality gate before declaring any task
  done. Checks lint, type, tests (root + MCP), forbidden patterns, feature
  branch, and commits. Use as the final pre-PR check.
allowed-tools: Bash(uv run poe check), Bash(uv run poe ci), Bash(uv run pytest *), Bash(git status), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(grep *), Read
---

# /quality-gate — CLAUDE.md Zero-Tolerance Pre-Done Check

Mandatory checklist that mirrors CLAUDE.md's Mandatory Completion Checklist. Run this before declaring any task complete.

## PURPOSE

Confirm the work is actually done by CLAUDE.md's standard: all tests pass, all linting passes, no shortcuts taken, on a feature branch, committed.

## CRITICAL

- **Pre-existing issues are NOT excuses** — if `uv run poe check` fails because of a test that was already broken, fix it before declaring the task done. CLAUDE.md is explicit: "ALL tests must pass, regardless of when the issues were introduced."
- **No `# noqa`, no `# type: ignore`, no skipped tests** — these are forbidden shortcuts. Refactor instead.
- **MCP server tests are NOT covered by `uv run poe check`** — they live in `stocktrim_mcp_server/tests/`. Run them separately if MCP code changed.
- **Must be on a feature branch** with all changes committed before this skill returns success.

## STANDARD PATH

### 1. Working tree status

```bash
git status
git branch --show-current
```

- Branch must NOT be `main`. If it is, stop and create a feature branch.
- Working tree should be clean (everything committed). If not, commit before proceeding.

### 2. Run `uv run poe check`

```bash
uv run poe check
```

This runs `format-check`, `lint` (ruff + ty + yaml), and `test` for the root package. ALL must pass. Any failure — even one labeled "pre-existing" — is a blocker.

### 3. Run MCP server tests if relevant

If any file under `stocktrim_mcp_server/` changed (check `git log main..HEAD --name-only`):

```bash
cd stocktrim_mcp_server && uv run pytest -x
```

ALL must pass.

### 4. Forbidden-pattern scan

```bash
git diff main...HEAD | grep -E '^\+.*(# noqa|# type: ?ignore|@pytest\.mark\.skip)' || echo "OK"
git diff main...HEAD -- 'stocktrim_public_api_client/generated/' 'stocktrim_public_api_client/client_types.py' || echo "OK"
git log main..HEAD --format='%s' | grep -E -- '--no-verify|--no-edit' || echo "OK"
```

Each command should print `OK` (no matches). If any prints lines from the diff, you've taken a forbidden shortcut — fix before declaring done.

### 5. Commit hygiene

```bash
git log main..HEAD --oneline
```

- At least one commit beyond `main`.
- Each subject follows conventional format: `feat(client):`, `fix(mcp):`, `chore:`, `docs:`, `test:`, `refactor:`.
- Subjects are descriptive — no `wip`, no `fix stuff`, no `update`.

### 6. Output

Report a checklist with ✅/❌ for each item:

```
✅ On feature branch (chore/foo)
✅ Working tree clean
✅ uv run poe check: passes
✅ MCP tests: passes (or N/A — no MCP changes)
✅ No # noqa / # type: ignore added
✅ No edits to generated/ or client_types.py
✅ Commits use conventional format

Result: READY (or NOT READY — list specific failures)
```

If NOT READY, list each failing check and stop. Do not declare the task done.

## EDGE CASES

- [`uv run poe check` fails on something unrelated] — Per CLAUDE.md: fix it. "Unrelated to my changes" is not a valid excuse. Open a sibling commit if needed.
- [Tests timing out] — Default timeout is 30s; if a test legitimately needs more, set `@pytest.mark.timeout(60)` on the specific test (not via global config). Never `pytest.mark.skip`.
- [MCP test suite has its own broken pre-existing tests] — Same rule: fix them. If the user pushes back, ask for permission to skip — never skip silently.

## RELATED

- `/commit` — Quality-gated conventional commits (this skill is the gate)
- `/open-pr` — Runs `quality-gate` implicitly via `discover-verification-cmd.sh`
- `verifier` agent — Lighter-weight version of this same checklist
- CLAUDE.md "MANDATORY COMPLETION CHECKLIST" — the source of truth
