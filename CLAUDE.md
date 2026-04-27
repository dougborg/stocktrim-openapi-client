# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

This is a **Python client library and MCP server** for the StockTrim Inventory
Management API. The repository contains:

1. **Client Library** (`stocktrim_public_api_client/`): OpenAPI-generated client with
   transport-layer resilience
1. **MCP Server** (`stocktrim_mcp_server/`): Model Context Protocol server for AI
   integration
1. **Documentation** (`docs/`): Comprehensive guides and architecture decisions

## Development Commands

This project uses **uv** with **poethepoet** task runner. All development tasks are
defined in `[tool.poe.tasks]` section of `pyproject.toml`.

### Setup

```bash
uv sync                          # Install all dependencies (includes poethepoet)
uv run poe pre-commit-install    # Setup pre-commit hooks
```

### Code Quality

```bash
uv run poe lint                  # Lint code with ruff, type check with ty, and lint YAML files
uv run poe lint-ruff-fix         # Auto-fix linting issues
uv run poe format                # Format code with ruff
uv run poe lint-ty               # Type check with ty (Astral's fast type checker)
```

## CRITICAL: Zero Tolerance for Ignoring Errors - ABSOLUTE REQUIREMENT

**NEVER say "but these were pre-existing issues so they are fine to ignore" or ANYTHING
like that. This is FORBIDDEN.**

When asked to fix linting, type checking, or test errors:

- **FIX THE ACTUAL ISSUES** - do not use `noqa`, `type: ignore`, exclusions, or skips
- **NO SHORTCUTS** - do not exclude files from linting, skip tests, or ignore type
  errors
- **NO EXCUSES** - "unrelated to my changes" is not a valid reason to ignore errors
- **NO RATIONALIZING** - if you think you have a good reason to ignore an error, you are
  wrong
- **AGENT CODE IS NOT SACRED** - code written by agents must meet the same quality
  standards
- **REFACTOR INSTEAD** - if a function has too many parameters, use a dataclass; if a
  name conflicts with a built-in, rename it
- **ASK FIRST** - only use ignores/exclusions after explicitly asking and receiving
  permission
- **PRE-EXISTING ISSUES ARE NOT EXCUSES** - ALL tests must pass, ALL linting must pass,
  regardless of when the issues were introduced
- If you are unsure how to fix an error properly, ask the user for guidance
- The only acceptable solution is fixing the root cause of the error

**Examples of proper fixes:**

- Too many function parameters (PLR0917)? → Create a dataclass to group related
  parameters
- Method name shadows built-in (type checker error)? → Rename the method (e.g., `list()`
  → `find_all()`)
- Import causing circular dependency? → Restructure the code or use `TYPE_CHECKING`
  block

### MANDATORY COMPLETION CHECKLIST

**Before ANY coding task is considered complete, ALL of the following MUST be true:**

1. **ALL tests pass** - This includes:

   - Tests for new code you wrote
   - ALL existing tests (even if they were broken before)
   - Tests that seem unrelated to your changes
   - Integration tests, unit tests, all test suites
   - **NO EXCEPTIONS** - if a test was broken before, fix it

1. **ALL linting and formatting pass** - This includes:

   - Ruff linting with zero errors
   - Code formatting with zero issues
   - Type checking with zero errors
   - **NO EXCEPTIONS** - if there were linting errors before, fix them

1. **Code is committed** - All changes must be committed to git with appropriate commit
   messages

1. **Code is pushed to a feature branch** - If not already on a feature branch, create
   one and push the changes

**Verification commands:**

```bash
# Run these and ensure ALL pass with zero errors
uv run poe check          # Lint, type-check, and test
uv run poe test           # All tests must pass
uv run poe lint           # All linting must pass
git status                 # Verify all changes are committed
git branch                 # Verify you're on a feature branch
```

### Testing

```bash
uv run poe test                  # Run client library tests with pytest
uv run poe test-mcp              # Run MCP server tests (stocktrim_mcp_server/tests/)
uv run poe test-coverage         # Run tests with coverage reports (HTML, terminal, XML)
```

`uv run poe check` runs both `test` and `test-mcp`, so the MCP server suite cannot regress silently when only the client lib is touched.

### Documentation

```bash
uv run poe docs-serve            # Serve docs with hot reload (MkDocs)
uv run poe docs-build            # Build static documentation
```

### Combined Workflows

```bash
uv run poe check                 # Run lint, type-check, and test
uv run poe ci                    # Full build pipeline (format-check, lint, test-coverage, docs-build)
uv run poe clean                 # Clean build artifacts and cache directories
```

**Note**: All tasks use `uv run poe <task-name>` format. The CI/CD pipeline also uses
this format for consistency.

## Architecture

### Core Structure

- **stocktrim_public_api_client/stocktrim_client.py**: Main client with transport-layer
  resilience
- **stocktrim_public_api_client/helpers/**: Domain helper classes for common operations
- **stocktrim_public_api_client/generated/**: Generated API client (DO NOT EDIT)
- **stocktrim_mcp_server/**: MCP server implementation

### Key Systems

**Transport-Layer Resilience**:

- Automatic retries with exponential backoff
- Error translation to domain exceptions

**Domain Helpers**:

- Ergonomic wrapper methods for common operations
- 15+ convenience functions across products, customers, inventory, orders

**MCP Server**:

- FastMCP implementation
- 5 tools across product, customer, and inventory domains
- Type-safe with Pydantic validation

## Project Standards

- **Python 3.11+** with strict typing (ty - Astral's fast type checker)
- **Ruff** for linting/formatting (comprehensive rule set)
- **Async/await** patterns for API calls
- **Semantic commits** with commitizen
- **UV** for dependency management
- **Poethepoet** for task running
- **100% CI isolation** - no external dependencies in tests

## Common Pitfalls

❌ **Don't do this:**

- Use `# noqa` or `# type: ignore` to suppress errors
- Skip tests or reduce coverage
- Commit without running quality checks
- Call real APIs in tests
- Leave debug code or commented sections
- Ignore pre-existing test failures or linting errors

✅ **Do this instead:**

- Fix the root cause of linting/type errors
- Add tests for new functionality
- Run quality checks before every commit
- Mock all external dependencies
- Remove all debug code before PR
- Fix ALL tests and linting issues, regardless of when they were introduced

## Agent Harness

This repo uses the [harness-kit](https://github.com/dougborg/harness-kit) plugin
for Claude Code, with project-specific extensions in `.claude/`. Provenance is
tracked in `.harness-lock.json`. Run `/harness-kit:harness` to audit, update, or
retro the harness.

### Skills

| Skill | Purpose |
| --- | --- |
| `/commit` | Quality-gated conventional commits (upstream) |
| `/feature-spec` | Spec before multi-file implementations (upstream) |
| `/open-pr` | Push, create PR, wait for CI, address first round (upstream) |
| `/code-reviewer` | Six-dimension review with project-specific BLOCKING rules |
| `/skill-writer` | Author new skills with progressive disclosure (upstream) |
| `/standup` | Git/GitHub activity recap (upstream) |
| `/regenerate-client` | Run the OpenAPI regeneration pipeline + commit |
| `/add-nullable-field` | Patch `NULLABLE_FIELDS` and regenerate (no `# type: ignore`) |
| `/add-helper-method` | Add a typed helper that wraps a generated call |
| `/add-mcp-tool` | Add an MCP tool + service + test |
| `/quality-gate` | CLAUDE.md zero-tolerance pre-done checklist |

### Agents

| Agent | Purpose | Model |
| --- | --- | --- |
| `code-reviewer` | Pre-PR review (6 dimensions + StockTrim-specific blockers) | sonnet |
| `verifier` | Final-gate check: validation, branch, no shortcuts | haiku |
| `test-writer` | Pytest tests with httpx transport mocks | sonnet |
| `domain-advisor` | Read-only Q&A on StockTrim API quirks, retry policy, auth | sonnet |
| `project-manager` | GitHub issues, PRs, releases, dependabot triage | sonnet |

### Automation Philosophy

`.claude/settings.json` configures PostToolUse hooks in three tiers:

1. **Formatters** (silent, zero-token) — `ruff check --fix` and `ruff format` run
   automatically on every Python edit so style issues never reach Claude.
2. **Validators** (bounded, gated) — `ty check` and per-file `pytest` run on the
   touched file only; output is capped at ≤25 lines so noise never drowns signal.
3. **Guidance** (≤20 lines) — generated/ edits, regenerate_client.py changes,
   and OpenAPI spec touches print a one-line nudge pointing to the right skill.

A Stop hook nudges toward `/harness-kit:harness retro` after sessions touching
more than three files. Never silence these by removing them — fix the cause they
surface.
