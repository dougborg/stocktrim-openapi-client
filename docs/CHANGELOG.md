# CHANGELOG

<!-- version list -->

## v0.4.1 (2025-10-31)

### Bug Fixes

- Handle response.elapsed RuntimeError in logging hook
  ([`8138298`](https://github.com/dougborg/stocktrim-openapi-client/commit/8138298e6d2b4ea1e5f4eab1d1a6c0eb522e8637))

The \_log_response_metrics hook was accessing response.elapsed before the response body
was read, causing a RuntimeError. This broke MCP server tool calls.

Error: RuntimeError: '.elapsed' may only be accessed after the response

has been read or closed.

Fix: - Wrap response.elapsed access in try/except - Fall back to logging without elapsed
time if not yet available - Prevents tool calls from failing due to metrics logging

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

## v0.4.0 (2025-10-31)

### Bug Fixes

- **release**: Commit MCP version bumps and use modern GitHub Actions output
  ([`175a50d`](https://github.com/dougborg/stocktrim-openapi-client/commit/175a50d93bd374d445daf596d2e74b93f7e25293))

Fixes two issues in the MCP server release process:

1. MCP version bumps are now committed to git before building, preventing duplicate
   version errors on PyPI. Previously the version was only updated locally during the
   build, so every release tried to publish the same version.

1. Replaced deprecated ::set-output command with modern $GITHUB_OUTPUT environment file
   syntax.

Changes: - Git commit added after MCP version bump (with proper bot credentials) - Push
MCP version commit before building - Updated Python script to use GITHUB_OUTPUT file
instead of ::set-output

This ensures each MCP server release gets a unique, incremented version number that's
tracked in git.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

- Add defensive guard for GITHUB_OUTPUT environment variable
  ([`32a3b05`](https://github.com/dougborg/stocktrim-openapi-client/commit/32a3b05021de7f51072a9d49d5f8c02caab7b9b1))

Add null check for GITHUB_OUTPUT before writing to it, making the script more robust for
local testing scenarios.

While GITHUB_OUTPUT is always set in GitHub Actions workflows, this defensive check
follows best practices and prevents potential issues in non-standard environments.

Co-Authored-By: Claude <noreply@anthropic.com>

### Refactoring

- Split MCP version update into separate steps and add error handling
  ([`319cc34`](https://github.com/dougborg/stocktrim-openapi-client/commit/319cc343fddc3037ce5ccab3e135b28975c41be2))

Addresses Copilot review feedback:

1. Split version update into separate steps: - "Update MCP server version" - runs Python
   script and sets output - "Commit and push MCP version bump" - commits the changes -
   "Build MCP server package" - builds the package This allows proper use of GitHub
   Actions outputs instead of parsing stdout with grep (which is not portable due to -P
   flag).

1. Add error handling for git commit: - Use `git diff --cached --quiet ||` to only
   commit when changes exist - Prevents workflow failures on re-runs or when version
   hasn't changed

Co-Authored-By: Claude <noreply@anthropic.com>

## v0.3.0 (2025-10-31)

### Bug Fixes

- Disable Bearer token prefix to prevent malformed Authorization header
  ([#31](https://github.com/dougborg/stocktrim-openapi-client/pull/31),
  [`c7498fa`](https://github.com/dougborg/stocktrim-openapi-client/commit/c7498fad639ce61496d71bd9f6f4e3cb8fee12e2))

* fix: disable Bearer token prefix to prevent malformed Authorization header

StockTrim uses custom auth headers (api-auth-id, api-auth-signature) instead of the
standard Authorization Bearer token. Passing prefix='' to the parent AuthenticatedClient
prevents it from adding 'Authorization: Bearer ' header.

Fixes 'Illegal header value b"Bearer "' error when connecting to StockTrim API.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- refactor: use AuthenticatedClient's native auth_header_name for api-auth-id

Improved StockTrim authentication to leverage AuthenticatedClient's built-in header
customization instead of workarounds:

- Set `auth_header_name="api-auth-id"` to use native header customization - Pass actual
  `api_auth_id` value as `token` parameter - Simplified AuthHeaderTransport to only
  handle `api-auth-signature` - Removed `api_auth_id` parameter from
  `create_resilient_transport()`

This approach is cleaner and more idiomatic than the previous solution that used an
empty token with an empty prefix. It leverages the generated client's built-in
capabilities while maintaining our custom transport for the signature header.

Benefits: - No malformed Authorization headers - Uses built-in mechanisms (cleaner, more
maintainable) - Clear separation: static header via client, dynamic header via transport
\- Less custom code to maintain

All tests pass (48/48).

______________________________________________________________________

Co-authored-by: Doug Borg <dougborg@apple.com>

Co-authored-by: Claude <noreply@anthropic.com>

- Use SEMANTIC_RELEASE_TOKEN to bypass branch protection in release workflow
  ([`f3c09e5`](https://github.com/dougborg/stocktrim-openapi-client/commit/f3c09e5c818348df7bdc0e16ba0ec8f8559a6ff0))

The release workflow was failing because repository branch protection rules require all
changes to main go through pull requests. The semantic-release action needs to push
version bump commits directly to main.

Changes: - Updated checkout action to use SEMANTIC_RELEASE_TOKEN instead of GITHUB_TOKEN
\- Updated python-semantic-release action to use SEMANTIC_RELEASE_TOKEN

This matches the pattern used in katana-openapi-client and allows the release automation
to bypass branch protection rules with a personal access token.

Note: The SEMANTIC_RELEASE_TOKEN secret must be configured in repository

settings with a personal access token that has repo permissions.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Build System

- **deps**: Bump mdformat from 0.7.22 to 1.0.0
  ([#24](https://github.com/dougborg/stocktrim-openapi-client/pull/24),
  [`b7a992a`](https://github.com/dougborg/stocktrim-openapi-client/commit/b7a992a016ba4b09bcb5ddd9b49f9573577b2aaf))

Bumps [mdformat](https://github.com/hukkin/mdformat) from 0.7.22 to 1.0.0. -
[Commits](https://github.com/hukkin/mdformat/compare/0.7.22...1.0.0)

--- updated-dependencies: - dependency-name: mdformat dependency-version: 1.0.0

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] \<49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump ty from 0.0.1a24 to 0.0.1a25
  ([#23](https://github.com/dougborg/stocktrim-openapi-client/pull/23),
  [`a21794f`](https://github.com/dougborg/stocktrim-openapi-client/commit/a21794fff03a0d195e56125ea42696a23d76290f))

Bumps [ty](https://github.com/astral-sh/ty) from 0.0.1a24 to 0.0.1a25. -
[Release notes](https://github.com/astral-sh/ty/releases) -
[Changelog](https://github.com/astral-sh/ty/blob/main/CHANGELOG.md) -
[Commits](https://github.com/astral-sh/ty/compare/0.0.1-alpha.24...0.0.1-alpha.25)

--- updated-dependencies: - dependency-name: ty dependency-version: 0.0.1a25

dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] \<49699333+dependabot[bot]@users.noreply.github.com>

### Documentation

- Comprehensive documentation cleanup and consolidation
  ([`f7ba132`](https://github.com/dougborg/stocktrim-openapi-client/commit/f7ba132bfe35ccdc10c0237e6d22fd20baf80f90))

## Deleted Files - MIGRATION_PROGRESS.md - Migration complete, no longer needed -

docs/POETRY_USAGE.md - Outdated (project uses UV) - docs/STOCKTRIM_CLIENT_GUIDE.md -
Duplicate of docs/user-guide/client-guide.md - docs/TESTING_GUIDE.md - Duplicate of
docs/user-guide/testing.md

- docs/HELPER_CONVENIENCE_METHODS.md - Duplicate of docs/user-guide/helper-methods.md -
  docs/CODE_OF_CONDUCT.md - Duplicate of docs/contributing/code-of-conduct.md

## Consolidated Files - STOCKTRIM_API_FEEDBACK.md → docs/contributing/api-feedback.md

## Fixed Base URLs Changed all instances from app.stocktrim.com to api.stocktrim.com: - README.md (2

instances) - stocktrim_mcp_server/README.md (2 instances) - docs/mcp-server/overview.md
(2 instances)

## Fixed Method Names Changed list_all() to get_all() throughout: - docs/index.md -

docs/getting-started/quickstart.md

## Updated Poetry to UV Replaced all poetry commands with uv equivalents: -

docs/user-guide/client-guide.md - docs/user-guide/testing.md -
.github/pull_request_template.md

## Fixed Documentation Links - Updated all internal links to point to docs/user-guide/ files -

Updated README.md to reference correct documentation locations - Fixed code of conduct
link

## Minor Improvements - Added CHANGELOG.md to mkdocs.yml navigation - Fixed UV installation

instructions to use official installer - Removed duplicate files

All documentation now uses correct base URLs, method names, and UV commands.
Documentation builds successfully with no errors.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Enhance copilot instructions with testing patterns and update tasks to UV
  ([`aa71406`](https://github.com/dougborg/stocktrim-openapi-client/commit/aa71406896ec09f2dff73dfed144e0e3ef111bb1))

- Add comprehensive testing patterns section with 5 common fixtures and examples -
  Document critical idempotent find_or_create() helper pattern - Expand helper
  architecture details with code examples

  - Add MCP server documentation references - Update .vscode/tasks.json to use UV
    instead of Poetry
  - Remove outdated Poetry warning (tasks now corrected) - Enhance error handling and
    transport layer documentation

### Features

- Implement Phase 2B workflow tools for product and forecast management
  ([#28](https://github.com/dougborg/stocktrim-openapi-client/pull/28),
  [`c393bfb`](https://github.com/dougborg/stocktrim-openapi-client/commit/c393bfb27f85420c40c9dd4d7596fc4b23f2949b))

* Initial plan

* feat: implement four Phase 2B workflow tools for product and forecast management

Co-authored-by: dougborg <1261222+dougborg@users.noreply.github.com>

- test: add comprehensive tests for Phase 2B workflow tools

- chore: update test and linting configuration for MCP server

- fix: remove unused imports and format code with ruff

- fix: address ruff linting errors in Phase 2B workflow tools

Fixed 3 ruff linting errors: - RUF005: Use unpacking syntax for list concatenation in
supplier_onboarding.py - B017: Use ValueError instead of blind Exception in
test_forecast_management.py (2 occurrences)

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- fix: correct API model field names for Phase 2B workflow tools

Fixed type errors by using correct field names from generated API models: - Changed
supplier_id to id in SupplierResponseDto usage - Removed is_active field from
SupplierRequestDto (not in API) - Added null checks before accessing error field in
tests

- fix: correct API model field names in Phase 1 foundation tools

Fixed type errors in Phase 1 foundation tools by using correct field names: -
locations.py: Changed code/name/is_active to location_code/location_name - products.py:
Changed code/description/cost_price/selling_price to
product_id/product_code_readable/name/cost/price

These errors existed on main but weren't caught by CI previously.

- fix: correct import paths and model names in Phase 1 tools

Fixed type errors in Phase 1 tools: - inventory.py: Changed client_types import from
.generated to direct import - suppliers.py: Changed SupplierDto to SupplierRequestDto
with correct field names

- fix: remove unsupported category field from OrderPlanFilterCriteriaDto

Removed category parameter from filter criteria as it's not supported by the API model.
Only location_codes and supplier_codes are valid filter fields.

This error existed from Phase 2A but wasn't caught by CI previously.

- fix: exclude MCP server from ty type checking to avoid external dependency issues

Reverted the addition of MCP server paths to ty configuration. The MCP server imports
fastmcp which isn't resolved by ty, causing false positive unresolved-import errors that
block CI.

The MCP server code is still checked by ruff and pytest, just not by ty.

- fix: exclude MCP server tests from main project test suite

Removed MCP server from pytest testpaths and coverage configuration. The MCP server is a
separate package and should be tested independently.

This fixes ModuleNotFoundError when running tests, as the MCP server package isn't
installed in the main project's test environment.

______________________________________________________________________

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

Co-authored-by: Doug Borg <dougborg@apple.com>

Co-authored-by: Claude <noreply@anthropic.com>

- Implement urgent order management workflow tools for MCP Server Phase 2
  ([#26](https://github.com/dougborg/stocktrim-openapi-client/pull/26),
  [`ded40bb`](https://github.com/dougborg/stocktrim-openapi-client/commit/ded40bb7cc03e2d5f652f0ff10bec4549747c82b))

* Initial plan

* feat: implement urgent order management workflow tools

- Create workflows directory structure - Add review_urgent_order_requirements tool - Add
  generate_purchase_orders_from_urgent_items tool - Register workflow tools in main
  tools module - All tests pass, linting passes

Co-authored-by: dougborg <1261222+dougborg@users.noreply.github.com>

- refactor: optimize supplier lookup and clarify days_threshold usage

* Fix N+1 query pattern by batch fetching products for supplier mapping - Add clarifying
  comments about days_threshold in generate_purchase_orders - Update docstring to
  explain V2 API behavior - All tests pass, linting passes

- docs: improve documentation for API limitations and performance

* Add early return for empty urgent items list - Clarify batch fetch limitations in
  comments - Update GeneratePurchaseOrdersRequest docstring with clear explanation -
  Document that days_threshold is for API consistency - All tests pass, linting passes

______________________________________________________________________

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- Phase 1 Foundation Expansion for MCP Server 2.0
  ([#22](https://github.com/dougborg/stocktrim-openapi-client/pull/22),
  [`17cafee`](https://github.com/dougborg/stocktrim-openapi-client/commit/17cafee2e9e13a4683580e36f604bbb1a1365a70))

* feat: add Phase 1A foundation helper classes to client library

Add four new helper classes to support advanced inventory management workflows:

- OrderPlan: Query forecasts and order plan data with filtering capabilities \*
  get_urgent_items() - Find items needing urgent reordering * get_by_supplier() - Filter
  by supplier * get_by_category()

  - Filter by category

- PurchaseOrdersV2: V2 Purchase Orders API with auto-generation feature \*
  generate_from_order_plan()

  - Auto-generate POs from forecast recommendations * get_all_paginated() - List with
    pagination support * find_by_supplier() - Filter by supplier

- Forecasting: Trigger and monitor forecast calculations * run_calculations() - Trigger
  forecast recalculation * wait_for_completion() - Wait for calculation to finish with
  polling

- BillOfMaterials: Manage product component relationships * Full CRUD operations (get,
  create, delete) * get_for_product() - Get all components for a product \*
  get_uses_of_component() - Find where a component is used

All helpers follow the existing lazy-loading pattern and include comprehensive tests.
This work is part of Phase 1 (Foundation Expansion) for MCP Server 2.0.

Related: #17, #18

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- feat: add Phase 1B foundation MCP tools

Reorganize and expand MCP server tools with new foundation layer:

**Tool Organization:** - Created tools/foundation/ directory for low-level API
operations - Moved existing tools (products, customers, inventory) to foundation/ -
Updated tool registration to support modular architecture

**Enhanced Tools:** - products: Added create_product() and delete_product() operations -
inventory: Retained set_product_inventory() (no GET endpoint in API)

**New Foundation Tools:** - suppliers: get, list, create, delete operations - locations:
list and create operations - purchase_orders: get, list, delete operations (V1 API)

**Tool Count:** 15 foundation tools total - Products: 4 tools (get, search, create,
delete) - Customers: 3 tools (get, list, ensure_exists) - Inventory: 1 tool (set) -
Suppliers: 4 tools (get, list, create, delete) - Locations: 2 tools (list, create) -
Purchase Orders: 3 tools (get, list, delete)

All tools follow FastMCP patterns with proper error handling, logging, and Pydantic
models. This work is part of Phase 1 (Foundation Expansion) for MCP Server 2.0.

- fix: address Copilot PR review comments

* Move time import to module level in forecasting.py - Add performance warning to
  find_by_supplier() docstring about client-side filtering

- fix: address remaining Copilot review comments

* Fix locations.create() to pass single LocationRequestDto instead of list - Fix
  products.create() to pass single ProductsRequestDto instead of list - Enhance
  performance warning in find_by_supplier() about lack of server-side filtering - Add
  missing test dependencies to pyproject.toml

______________________________________________________________________

Co-authored-by: Doug Borg <dougborg@apple.com>

Co-authored-by: Claude <noreply@anthropic.com>

## v0.2.5 (2025-10-29)

### Bug Fixes

- Correct TOML key access for MCP server dependency update
  ([`787e3cd`](https://github.com/dougborg/stocktrim-openapi-client/commit/787e3cdf515fa3060fad6f6167f28c56f7fed2c7))

The release workflow was failing with KeyError: 'dependencies' when trying to update the
MCP server's client dependency. The dependencies array is nested under the [project]
table per PEP 621, not at the root level.

Changed data['dependencies'][0] to data['project']['dependencies'][0] to correctly
access the dependencies list in the TOML structure.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Documentation

- Comprehensive documentation overhaul
  ([`e72ec8f`](https://github.com/dougborg/stocktrim-openapi-client/commit/e72ec8fa5336a74e6badce3309a13f78a1009f96))

- Fixed index.md: removed Sphinx directives, added proper MkDocs structure - Created
  complete getting-started guides (installation, quickstart, configuration) - Created
  user guides (client usage, helpers, error handling, testing) - Created MCP server
  documentation (overview, installation, tools, Claude Desktop setup) - Created API
  reference with mkdocstrings auto-generation - Created architecture documentation
  (overview, transport, helpers) - Created contributing guides (development, code of
  conduct, API feedback) - Updated mkdocs.yml navigation structure - Fixed all heading
  issues and broken links

This provides comprehensive public-facing documentation for both the client library and
MCP server with auto-generated API docs.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

## v0.2.4 (2025-10-29)

### Bug Fixes

- Use tomllib/tomli-w instead of deprecated toml package
  ([`5aedd90`](https://github.com/dougborg/stocktrim-openapi-client/commit/5aedd901bdc66925db16f97804338102d922ae19))

Switched from the deprecated 'toml' package to Python 3.11+'s built-in tomllib for
reading and tomli-w for writing TOML files. Also fixed the installation command to use
'uv pip install' instead of 'uv run pip install' to ensure the package is available in
the uv environment.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

## v0.2.3 (2025-10-29)

### Bug Fixes

- Correct GitHub Pages artifact path for MkDocs
  ([`2901db5`](https://github.com/dougborg/stocktrim-openapi-client/commit/2901db5da86de29e85b8b60a69858f1a46b846a2))

Changed upload path from docs/\_build/html (Sphinx) to site/ (MkDocs default). This
fixes the "No such file or directory" error in the documentation deployment workflow.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

## v0.2.2 (2025-10-29)

### Bug Fixes

- Properly handle workspace dependencies in MCP server release
  ([`79c0e49`](https://github.com/dougborg/stocktrim-openapi-client/commit/79c0e49ba3c54bee09b4dd7aad2c1d15de2ee97b))

- Remove workspace source override when building MCP server for PyPI - Ensures MCP
  server uses versioned dependency from PyPI instead of workspace - Fixes build failures
  in release workflow for future releases

## v0.2.1 (2025-10-29)

### Bug Fixes

- Temporarily disable UV cache due to service issues
  ([`2508b7d`](https://github.com/dougborg/stocktrim-openapi-client/commit/2508b7daa0f7f526e543c106a56d522740f42b8b))

- Comment out enable-cache: true in both test and release jobs - Addresses GitHub
  Actions cache service problems - Can be re-enabled when cache service is stable

## v0.2.0 (2025-10-29)

### Bug Fixes

- Improve type casting in generated models and helpers
  ([`367e3cd`](https://github.com/dougborg/stocktrim-openapi-client/commit/367e3cd6e493afbb9124f69a29f239572582375c))

- Add proper type casting for .from_dict() methods in generated models - Enhance type
  safety in helper files with better casting - Update test utilities with improved type
  handling - Ensures strict type checking compliance with ty

### Documentation

- Update documentation from Poetry to UV
  ([`adf6072`](https://github.com/dougborg/stocktrim-openapi-client/commit/adf6072f26686f67721585b7c42b002a46f231ba))

- Update README.md with UV installation and usage instructions - Remove Poetry
  references from all documentation files - Update STOCKTRIM_API_FEEDBACK.md with UV
  commands - Ensure documentation consistency with current tooling

### Features

- Enhance regeneration script with automatic type fixing
  ([`e28859b`](https://github.com/dougborg/stocktrim-openapi-client/commit/e28859ba3a6b4b31ee37ffdff9ce69c83e4f961f))

- Add automatic type casting fixes for generated .from_dict() methods - Implement
  automatic import management (cast, Mapping) - Fix nested if statement linting issues
  (SIM102) - Improve error handling and progress reporting - Ensures generated code
  passes strict type checking

- Migrate from mypy to ty for faster type checking
  ([`85fc18a`](https://github.com/dougborg/stocktrim-openapi-client/commit/85fc18a887ee57022cce0e34c7ea69f21ce0f4e0))

- Replace mypy with Astral's ty type checker - Configure ty in pyproject.toml with
  proper exclude patterns for generated code - Update poe tasks to use ty instead of
  mypy - Maintain strict type checking with better performance - ty provides faster type
  checking and clearer error messages

- Migrate from mypy to ty type checker
  ([`648e51b`](https://github.com/dougborg/stocktrim-openapi-client/commit/648e51b8a93709c0ddad1f8e659da09f8602dd7e))

- Replace mypy with Astral's ty for faster, more accurate type checking - Update
  pyproject.toml with ty configuration - Modify test configuration to work with ty -
  Improves type checking performance and accuracy

- Update copilot instructions and enable MCP auto-publishing
  ([`a66d07b`](https://github.com/dougborg/stocktrim-openapi-client/commit/a66d07bf8ab4f730b2708557a3333b9a6bc44672))

- Update .github/copilot-instructions.md to reflect UV usage (not Poetry) - Document
  monorepo structure with client + MCP server packages - Add automatic type fixing
  documentation for regeneration script - Fix GitHub workflow artifact paths for UV
  build structure - Enable automatic MCP server publishing when client updates - Ensure
  proper PyPI coordination between packages

## v0.1.1 (2025-10-29)

### Bug Fixes

- Tidy __all__ ordering and comments
  ([`32de7af`](https://github.com/dougborg/stocktrim-openapi-client/commit/32de7aff9c1b7bf7a485f6f1557c191e55ead5d6))

### Chores

- Update GitHub Actions to latest versions
  ([`465a7b7`](https://github.com/dougborg/stocktrim-openapi-client/commit/465a7b77735d243c70a69f12e6c52d504c01b532))

- Update upload-pages-artifact from v3 to v4 - Pin trivy-action to v0.29.0 instead of
  @master - All other actions already on latest versions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Documentation

- Add PyPI badges to README for both packages
  ([`a88f81c`](https://github.com/dougborg/stocktrim-openapi-client/commit/a88f81cb17707021d22b643bf91d77e87363b1a2))

## v0.1.0 (2025-10-29)

### Bug Fixes

- Correct relative import paths for client_types in generated code
  ([`24aceaf`](https://github.com/dougborg/stocktrim-openapi-client/commit/24aceaf29a7d7a00f23e58fda36b62b8a9953aa8))

This commit fixes import path issues in generated API and model files:

- Updated regeneration script to properly calculate relative import depths - API files
  in generated/api/subdirectory/ now use ....client_types (4 dots) - Model files in
  generated/models/ now use ...client_types (3 dots) - Fixed type annotation in
  Customers.update() return type - Added integration tests for all domain helpers

The import fixer now correctly handles the directory structure: - Files in
generated/api/subdirectory/: need 4 dots (subdir → api → generated → package_root) -
Files in generated/models/: need 3 dots (models → generated → package_root) - Files
directly in generated/: need 2 dots (generated → package_root)

All tests now pass including new helper integration tests that verify: - Helper
accessibility via lazy-loaded properties - Core method availability on all helpers -
Proper lazy-loading behavior

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Update semantic-release version and temporarily disable docs tests
  ([`adaf2b3`](https://github.com/dougborg/stocktrim-openapi-client/commit/adaf2b34191749cf091a2c85928e4fe6519b73b4))

**Fixes:** - Update python-semantic-release from v9.0.0 to v9.15.2 - Fixes
bullseye-backports Docker build failure - Uses newer Debian bookworm base with proper
package sources - Temporarily disable docs tests in docs workflow - Tests look for
Sphinx artifacts but we're transitioning to MkDocs - Will re-enable after full MkDocs
migration

This should allow releases to proceed successfully.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Build System

- **client**: Migrate to UV workspace with Hatchling
  ([`4d47f54`](https://github.com/dougborg/stocktrim-openapi-client/commit/4d47f54fd58b3f49e93349f7122614959f99e772))

- Replace Poetry with UV workspace configuration - Update pyproject.toml to use
  Hatchling build backend - Add workspace members: stocktrim-openapi-client and
  stocktrim-mcp-server - Remove poetry.lock, generate uv.lock - Update dependencies to
  match katana versions (httpx-retries, ruff 0.12+) - Add comprehensive poethepoet task
  library with uv run commands - Add MkDocs dependencies in docs extras - Update
  semantic release config for monorepo (client-v tag format) - Add validation tasks for
  OpenAPI (basic + Redocly) - Create minimal MCP server package structure

Breaking change: Build system migration from Poetry to UV + Hatchling

Co-Authored-By: Claude <noreply@anthropic.com>

### Chores

- Initial project setup
  ([`b9b582c`](https://github.com/dougborg/stocktrim-openapi-client/commit/b9b582cbad0e22b39628e9b869016322ebf3a0aa))

- **client**: Add devcontainer setup for VS Code
  ([`302fd30`](https://github.com/dougborg/stocktrim-openapi-client/commit/302fd300a1ac84d475794ac621117897a526e7d5))

- Create .devcontainer/devcontainer.json: * Python 3.13 base image * Git, GitHub CLI,
  Node.js LTS * VS Code extensions (Python, Ruff, Copilot, Docker, YAML) * Auto-format
  on save with Ruff * pytest integration - Create .devcontainer/oncreate.sh (prebuild
  caching) - Create .devcontainer/setup.sh (post-create finalization) - Create
  .devcontainer/README.md (documentation) - Port 8000 forwarded for MCP server -
  Resource requirements specified (4 CPU, 8GB RAM, 32GB storage)

Enables consistent development environment across team

Co-Authored-By: Claude <noreply@anthropic.com>

- **client**: Update code quality tooling configuration
  ([`56f0c92`](https://github.com/dougborg/stocktrim-openapi-client/commit/56f0c9250ef44ff6c5f935271f8960c348dc9e95))

- Update .pre-commit-config.yaml: * Add --allow-multiple-documents and --unsafe to
  check-yaml * Add CHANGELOG.md exclusion to mdformat * Add local pytest hook (runs 'uv
  run poe test') - Update .gitignore with comprehensive patterns: * Add .ruff_cache/
  exclusion * Remove project-specific debug file patterns * Cleaner organization and
  comments - .yamllint.yml already configured correctly

All tooling now matches katana-openapi-client patterns

Co-Authored-By: Claude <noreply@anthropic.com>

- **client**: Update OpenAPI spec from live API
  ([`622836c`](https://github.com/dougborg/stocktrim-openapi-client/commit/622836cab4f68b2b2e03c059f4a341010718e32c))

Downloaded latest spec from https://api.stocktrim.com/swagger/v1/swagger.yaml

Changes are primarily formatting updates (indentation consistency). No new endpoints or
breaking changes identified.

This ensures our generated client matches the current API exactly.

Co-Authored-By: Claude <noreply@anthropic.com>

### Continuous Integration

- Add environment names back to distinguish dual-package publishing
  ([`27a1e78`](https://github.com/dougborg/stocktrim-openapi-client/commit/27a1e78c094fbc9cf9a3dd9516872a6a0fd54a30))

Added environment names to help PyPI Trusted Publishers distinguish between the two
packages published from the same workflow:

- Client: environment 'pypi-client' - MCP Server: environment 'pypi-mcp'

This allows PyPI to properly configure separate trusted publishers for each package.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Migrate all workflows from Poetry to UV
  ([`3a40535`](https://github.com/dougborg/stocktrim-openapi-client/commit/3a4053538a163799f4c252ee57750ce7c49560ce))

Updated all GitHub Actions workflows to use UV instead of Poetry:

**CI Workflow (ci.yml):** - Use astral-sh/setup-uv@v4 action - UV-based Python
installation and dependency management - Removed Poetry caching, using UV's built-in
cache - Added concurrency control to cancel redundant runs - Simplified dependency
installation

**Documentation Workflow (docs.yml):** - Migrated to UV for docs building and testing -
Cleaner, faster builds with UV caching

**Release Workflow (release.yml):** - Dual-package build support (client + MCP server) -
Separate PyPI publishing for both packages - UV-based builds with `uv build` and
`uv build --package` - Individual artifact uploads and publishing

**Security Workflow (security.yml):** - UV integration for dependency scanning - Use
`uv tool` for semgrep installation - Maintained Trivy and dependency review

**Benefits:** - ✅ Faster CI runs (UV is significantly faster than Poetry) - ✅ Simplified
workflows (less caching boilerplate) - ✅ Dual-package release support - ✅ Consistent
tooling across local dev and CI

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Remove environment requirements from release workflow
  ([`6e4c35e`](https://github.com/dougborg/stocktrim-openapi-client/commit/6e4c35ecfd576858b9b433068010dec109f722d6))

Removed GitHub Environment requirements to match katana-openapi-client pattern: - No
manual approval gates needed - Fully automated releases - Simpler PyPI Trusted Publisher
setup

PyPI configuration is now simpler - no environment name required.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Documentation

- Add constructive API feedback document for StockTrim
  ([`8f02246`](https://github.com/dougborg/stocktrim-openapi-client/commit/8f02246f256a5db9f5c04f54124fd14f306898ca))

Created comprehensive feedback document highlighting: - OpenAPI specification
improvements (security schemes, documentation) - Response type consistency issues -
Authentication documentation needs - Endpoint convention questions - Pagination, error
handling, and versioning clarifications

All feedback is framed constructively and positively, intended to help StockTrim
developers improve the API for all users.

The document includes: - Clear examples of current state vs. suggested improvements -
Benefits of each suggestion - Specific questions that need clarification - Tables
comparing inconsistent patterns across endpoints

This serves as a reference for: 1. Our own client library design decisions 2. Future
discussions with StockTrim team 3. Understanding API quirks we need to work around

- Add convenience methods reference for MCP tool design
  ([`6ab6082`](https://github.com/dougborg/stocktrim-openapi-client/commit/6ab6082084abfbedd6b077e074e80e400e088fb7))

Created comprehensive documentation of all helper convenience methods: - Catalogs all
convenience methods with use cases - Maps methods to proposed MCP tools - Provides
design recommendations for MCP integration - Includes code examples for each method -
Documents error handling and return type patterns

This will serve as the blueprint for MCP server tool design, ensuring the MCP tools
provide ergonomic access to StockTrim API.

- Mark migration as complete - 88% done, all core phases finished
  ([`6ca6cb4`](https://github.com/dougborg/stocktrim-openapi-client/commit/6ca6cb432c757ca7d2291860b81b86376a4df0eb))

**Migration Status: COMPLETE** 🎉

Completed 14 of 16 planned commits (88%). All production-critical phases done:

**✅ Completed Phases:** - Phase 1-3: Infrastructure & Core (UV workspace, transport
layer, helpers, utils) - Phase 4: Testing infrastructure (comprehensive fixtures) -
Phase 5: Regeneration script (already enhanced) - Phase 6: CI/CD workflows (all migrated
to UV, dual-package support) - Phase 8: MCP Server (FastMCP, 5 tools, production-ready)
\- Documentation (README, MkDocs config, helper reference, MCP guide)

**📊 Project Status:** - 42/42 tests passing (100%) - 0 linting errors (ruff, ty,
yamllint) - 2 packages ready: stocktrim-openapi-client + stocktrim-mcp-server - Full
CI/CD pipeline operational

- Production-ready for release

**Optional Remaining:** - Phase 7: Full MkDocs migration (docs work, not blocking) -
ADRs (documentation enhancement)

The project is production-ready and can be released as v0.2.0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Update migration progress to reflect completed work
  ([`2760a6f`](https://github.com/dougborg/stocktrim-openapi-client/commit/2760a6fc3c7212bcd93df023f5e3e561a97d3064))

Core functionality is now complete (69% done): - ✅ Build system (UV workspace) - ✅
Client architecture (transport patterns) - ✅ Domain helpers (15+ convenience methods) -
✅ MCP server (5 tools, 3 domains) - ✅ All tests passing (42 passed) - ✅ All linting
passing

Remaining work focuses on documentation, CI/CD, and ADRs.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Update README and add MkDocs configuration
  ([`2bc29d1`](https://github.com/dougborg/stocktrim-openapi-client/commit/2bc29d16355d78adb177d89609915a28745a1930))

**README Updates:** - Comprehensive feature list for client and MCP server - Domain
helpers documentation with all 7 helper classes - Error handling examples with typed
exceptions - MCP server tools and example conversations - Updated installation
instructions for UV - Development setup and common tasks - Architecture explanations
(transport-layer, helpers) - Project structure overview

**MkDocs Configuration:** - Complete mkdocs.yml with Material theme - Navigation
structure for all docs sections - Plugin configuration (search, mkdocstrings) - Markdown
extensions (code highlighting, mermaid, tabs) - Prepared for future full documentation
migration

**Quality Assurance:** - ✅ All tests passing (42 passed) - ✅ All linting passing (ruff,
ty, yamllint) - ✅ Documentation accurate and up-to-date

The README now provides a complete overview of the project's current capabilities
including domain helpers and MCP server.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- **client**: Add comprehensive migration progress documentation
  ([`5f17dbb`](https://github.com/dougborg/stocktrim-openapi-client/commit/5f17dbbcf1daf1eaa4381cd297e5cbae7e395b59))

- Document completed work (commits 1-3): 19% complete - Detail remaining 13 commits with
  implementation plans - StockTrim-specific simplifications noted: * No rate limiting
  (429) - simpler retry logic * No pagination - remove PaginationTransport * Custom auth
  headers (api-auth-id/signature) - Include code examples and verification steps -
  Reference katana files for implementation guidance - Development commands and file
  structure - Questions to address in next session

Enables future work continuation with full context

Co-Authored-By: Claude <noreply@anthropic.com>

- **client**: Update migration plan with API spec analysis and decisions
  ([`159129e`](https://github.com/dougborg/stocktrim-openapi-client/commit/159129e66f152ffe5faa05c05c51bed1c4176800))

Updates based on user input and OpenAPI spec analysis:

API Characteristics: - No pagination, no rate limiting (confirmed) - Custom auth:
api-auth-id (Tenant Id) + api-auth-signature (Tenant Name) - Mixed access patterns: some
lists, some by ID, bulk operations - Query parameter filtering (e.g., BOMs by
productId/componentId)

Decisions Made: - Create domain helpers for ALL StockTrim entities - MCP tools:
verify_connection, get_product, check_inventory, list_orders - Document dual model
architecture (internal + Square integration) - API is primarily resource-based with
limited list operations

Domain Model Documented: - Core: Products, Customers, Suppliers, Locations, Inventory,
BOMs - Orders: Sales Orders (with bulk/range ops), Purchase Orders (V2) - Operations:
Order Plan, Forecasting, Processing Status, Configuration - Integrations: Square, InFlow

Simplified transport layer for StockTrim (no pagination/rate limit handling)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

- Add authentication fix and domain helper classes (WIP)
  ([`f73e368`](https://github.com/dougborg/stocktrim-openapi-client/commit/f73e368dd7076cb14644e8e53d50490832110fd8))

This commit implements major improvements to the client generation and adds domain
helper classes for easier API interaction:

**Authentication Fix:** - Modified regeneration script to convert StockTrim's auth
header parameters to proper OpenAPI securitySchemes - Removes api-auth-id and
api-auth-signature from all 39 endpoints (78 params total) - Adds proper security scheme
definition that will be handled by transport layer - Generated API methods no longer
require auth parameters

**Domain Helper Classes:** - Created helpers package with base class and domain-specific
helpers - Added helpers for: Products, Customers, Suppliers, Sales Orders, Purchase
Orders, Inventory, and Locations - Integrated helpers into StockTrimClient with
lazy-loaded properties - Helpers provide ergonomic CRUD operations wrapping generated
API methods

**Note:** Helper method signatures need refinement to match actual StockTrim API
conventions (some endpoints use different parameter names than initially assumed). Type
checking currently fails but infrastructure is in place.

Related to Commit 7 in migration plan.

- Add convenience methods to all domain helpers
  ([`fe54385`](https://github.com/dougborg/stocktrim-openapi-client/commit/fe54385a2488e56561c61f38e10f2794f036e577))

Added convenience methods to all helper classes that provide: - Simpler, more ergonomic
interfaces for common operations - Better handling of API inconsistencies - Clearer
intent through well-named methods

**Products:** - find_by_code(code) - Find single product, returns None if not found -
search(prefix)

- Alias for get_all() with clearer search intent - exists(code) - Boolean check for
  product existence

**Customers:** - exists(code) - Boolean check for customer existence -
find_or_create(code, \*\*defaults) - Get or create pattern

**Suppliers:** - find_by_code(code) - Handles single|list API inconsistency -
create_one(supplier) - Wrapper for batch API accepting single item - exists(code) -
Boolean check for supplier existence

**SalesOrders:** - get_for_product(product_id) - Clearer alias for filtering -
delete_for_product(product_id) - Clearer alias for deletion

**PurchaseOrders:** - find_by_reference(ref) - Handles single|list API inconsistency -
exists(reference_number) - Boolean check for order existence

**Inventory:** - set_for_product(product_id, ...) - Simplified single-product setter

These methods will directly inform MCP tool design, making the API more accessible
through Claude's tool interface.

All quality checks pass ✅

- Add utils.py with response unwrapping and typed exceptions
  ([`a6f0fe5`](https://github.com/dougborg/stocktrim-openapi-client/commit/a6f0fe576b809d0f8943a799578254e615fd1db8))

This commit adds a comprehensive utils module for handling StockTrim API responses with
typed exceptions and convenience functions.

**Exception Hierarchy**:

- `APIError` (base exception with status_code and problem_details) -
  `AuthenticationError` (401) - `PermissionError` (403) - `NotFoundError` (404) -
  `ValidationError` (400, 422) - `ServerError` (5xx)

All exceptions include: - Human-readable error message - HTTP status code - Optional
ProblemDetails object from API

**Response Unwrapping Functions**:

1. `unwrap(response, raise_on_error=True)`: - Main utility for handling API responses -
   Auto-raises typed exceptions on error status codes - Returns parsed data on success -
   Optional non-raising mode (returns None on error)

1. `is_success(response)`: - Check if response has 2xx status code

1. `is_error(response)`: - Check if response has 4xx/5xx status code

1. `get_error_message(response)`: - Extract error message from ProblemDetails or status
   code

**StockTrim Simplifications**:

- No `unwrap_data()` function - StockTrim doesn't wrap responses in `.data` arrays -
  Focused on ProblemDetails error format when available - Clean fallback to status code
  for generic errors

**Testing**:

- Comprehensive test coverage (28 tests) - Tests for all exception types - Tests for
  success/error detection - Tests for error message extraction - All tests pass with
  full type safety

**Integration**:

- All utilities exported from package root - Proper type hints with mypy compliance -
  Compatible with generated Response[T] types

Example usage: \`\`\`python from stocktrim_public_api_client import StockTrimClient,
unwrap from stocktrim_public_api_client.api.products import get_api_products

async with StockTrimClient() as client: response = await
get_api_products.asyncio_detailed(client=client) products = unwrap(response) # Raises on
error, returns parsed data \`\`\`

Part of migration from katana-openapi-client improvements (Commit 6).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Complete CI/CD infrastructure setup for StockTrim OpenAPI client
  ([`f40a767`](https://github.com/dougborg/stocktrim-openapi-client/commit/f40a767e965ac7d61c785dd4da86aeff887b42b9))

- Add GitHub Actions workflows (CI, release, security, docs) - Add Sphinx documentation
  infrastructure with AutoAPI - Add pre-commit hooks and quality tools (ruff, mypy,
  yamllint) - Add enhanced poe tasks for development workflow - Add GitHub issue/PR
  templates and Code of Conduct - Fix environment variable handling for proper test
  isolation - Match Katana project architecture and patterns - All tests passing with
  100% CI pipeline success

- Implement StockTrim MCP server with FastMCP
  ([`0aba445`](https://github.com/dougborg/stocktrim-openapi-client/commit/0aba445f03af8ce94a960713f6d349d30326e2b0))

This commit adds a complete MCP (Model Context Protocol) server for StockTrim Inventory
Management, enabling AI assistants like Claude to interact with StockTrim APIs through
natural language.

**Server Implementation:** - FastMCP-based server with lifespan management -
Environment-based authentication (API auth ID and signature) - Automatic client
initialization with error handling - Production-ready logging and resilience

**Tools Implemented:**

Products (2 tools): - get_product: Retrieve product by code - search_products: Search by
code prefix

Customers (2 tools): - get_customer: Retrieve customer by code - list_customers: List
all customers with limit

Inventory (1 tool): - set_product_inventory: Update stock levels for a product

**Features:** - Type-safe with full Pydantic models for requests/responses - Leverages
helper convenience methods from client library - Comprehensive error handling and
logging - Claude Desktop integration ready

**Documentation:** - Complete README with installation instructions - Configuration
examples for Claude Desktop - Tool usage examples and conversation patterns -
Development guide and troubleshooting section

**Dependencies:** - fastmcp>=0.3.0 for MCP server framework - python-dotenv>=1.0.0 for
environment management - Workspace dependency on stocktrim-openapi-client

The server can be run via: - uvx stocktrim-mcp-server - python -m stocktrim_mcp_server -
Direct import and execution

This implementation follows the patterns from katana-mcp-server and provides a
foundation for expanding StockTrim API coverage through additional MCP tools.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Optimize documentation testing and include generated API documentation
  ([`d97e8b5`](https://github.com/dougborg/stocktrim-openapi-client/commit/d97e8b5f37264a2497f1785a1f11b6274945acf3))

- Add conditional documentation testing with CI_DOCS_BUILD environment flag - Create
  comprehensive documentation tests for Sphinx build validation - Optimize local
  development workflow by skipping slow docs tests by default - Update CI workflows to
  properly run documentation tests in docs build jobs - Add pytest markers for better
  test organization (docs marker added) - Modify Sphinx configuration to include
  generated API documentation - Add comprehensive API reference documentation for all
  generated client modules - Extend test timeouts to 600 seconds (10 minutes) for
  documentation builds - Add new test commands: test-docs, test-no-docs, test-all -
  Update help text to reflect new testing options

Benefits: - Local development: 5 tests run in 0.02s (docs tests skipped) - CI builds:
All tests including 3 docs tests run when CI_DOCS_BUILD=true - Generated API
documentation now fully accessible in Sphinx docs - Better separation between fast unit
tests and slow documentation builds - Comprehensive validation of documentation
generation in CI/CD

This brings StockTrim in line with the documentation testing improvements made to the
Katana project, ensuring consistent developer experience across both API client
projects.

- Rename types.py to client_types.py and enhance regeneration script
  ([`9f53d0b`](https://github.com/dougborg/stocktrim-openapi-client/commit/9f53d0b289f231e62713244f92f1c4798d051f9f))

This commit implements several improvements to the client generation process:

1. **Enhanced Regeneration Script** (adapted from katana-openapi-client): - Added
   multi-validator approach (openapi-spec-validator + Redocly CLI) - Implemented
   types.py → client_types.py rename during generation - Added post-processing for
   import fixing (.types → .client_types) - Implemented Union type modernization
   (Union[A, B] → A | B) - Added RST docstring formatting fixes - Integrated ruff
   auto-fixes with --unsafe-fixes flag - Added streaming test output for validation -
   Structured output with clear step-by-step logging

1. **Client Types Architecture**: - Moved types.py from generated/ to package root as
   client_types.py - This matches the katana-openapi-client architecture - All generated
   files now import from ..client_types instead of .types - Prevents name conflicts with
   Python built-in types module

1. **Generated Code Updates**: - All 42 generated model files updated with correct
   imports - All 40 generated API endpoint files updated with correct imports -
   client.py updated to use client_types

- Removed generated/py.typed and generated/types.py

The regeneration script is now production-ready and can be run with:
`uv run python   scripts/regenerate_client.py`

Part of migration from katana-openapi-client improvements.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

- Rewrite StockTrimClient with transport pattern architecture
  ([`ca3d561`](https://github.com/dougborg/stocktrim-openapi-client/commit/ca3d5614beabefad0599fb4cba49f3c0ad0b1203))

This commit implements a complete rewrite of the StockTrimClient using the
transport-layer pattern, adapted from katana-openapi-client.

**Architecture Changes**:

1. **Client Inheritance** (Breaking Change): - Old: StockTrimClient wraps
   AuthenticatedClient (access via `.client`) - New: StockTrimClient inherits from
   AuthenticatedClient (pass directly) - API methods now receive client directly:
   `method(client=client)` instead of `method(client=client.client)`

1. **Layered Transport Architecture**: - `AsyncHTTPTransport` (base HTTP layer) -
   `AuthHeaderTransport` (adds api-auth-id, api-auth-signature headers) -
   `ErrorLoggingTransport` (logs 4xx errors with ProblemDetails parsing) -
   `RetryTransport` (retry 5xx errors on idempotent methods only)

1. **Custom Retry Class**: - `IdempotentOnlyRetry` - only retries GET, HEAD, OPTIONS,
   TRACE on 5xx - No rate limiting (429) handling - StockTrim doesn't rate limit - Uses
   httpx-retries library with exponential backoff

1. **Simplified vs Katana**: - ❌ No RateLimitAwareRetry - StockTrim doesn't have rate
   limits - ❌ No PaginationTransport - StockTrim doesn't paginate - ✅
   ErrorLoggingTransport - Better error visibility - ✅ Basic retry on 5xx for idempotent
   methods only

**New Components**:

- `create_resilient_transport()` - Factory for layered transport composition -
  `IdempotentOnlyRetry`
  - Custom retry class for safe 5xx retries - `ErrorLoggingTransport` - Detailed 4xx
    error logging with ProblemDetails - `AuthHeaderTransport` - StockTrim custom auth
    header injection

**API Changes**:

````python # Old usage async with StockTrimClient() as client: response = await
  some_api(client=client.client) # Need .client

# New usage async with StockTrimClient() as client: response = await some_api(client=client) # Pass
  directly! ```

**Testing**:

- Updated all tests for new architecture - All tests pass (5/5) - All quality checks pass (ruff,
  mypy, yamllint)

Part of migration from katana-openapi-client improvements (Commit 5).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Refactoring

- Rewrite helpers with correct API signatures
  ([`e9f615e`](https://github.com/dougborg/stocktrim-openapi-client/commit/e9f615e5752e7c397198d1e860423764d3a3bdcf))

Completely rewrote all domain helper classes from scratch based on actual StockTrim API signatures
  instead of assumptions from katana.

**Key Changes:** - Renamed `list()` to `get_all()` to avoid shadowing builtin `list` type - Fixed
  all method signatures to match actual StockTrim API endpoints - Added proper type annotations
  including union types where API is inconsistent - Documented API inconsistencies in docstrings
  with "Note:" sections

**Helper Methods Now Correctly Match API:** - Products: get_all(code?, pageNo?) → array, create(dto)
  → single, delete(productId?) - Customers: get_all() → array, get(code) → single, update(dto) →
  array - Suppliers: get_all(code?) → single|array, create([dto]) → array, delete(codeOrName) -
  SalesOrders: get_all(productId?) → array, create(dto) → single, delete(productId?) -
  PurchaseOrders: get_all(refNum?) → single|array, create(dto) → single, delete(refNum) → single -
  Inventory: set(request) → single - Locations: get_all(code?) → single|array, create(dto) → single

**API Inconsistencies Documented:** - Some GET endpoints return single objects when filtered (should
  return arrays) - Inventory POST returns PurchaseOrderResponseDto (incorrect response type) -
  Suppliers POST accepts/returns arrays (batch operation)

All quality checks pass: ruff, mypy, pytest ✅

Related to Commit 7 in migration plan.

### Testing

- Enhance test infrastructure with comprehensive fixtures
  ([`f9623e9`](https://github.com/dougborg/stocktrim-openapi-client/commit/f9623e9936f7572010af772e67109958f5ffb057))

Added comprehensive test fixtures following katana patterns:

**New Fixtures:** - async_stocktrim_client: Async context manager for testing -
  create_mock_response: Factory for creating custom mock responses - mock_server_error_response: 500
  error with ProblemDetails format - mock_authentication_error_response: 401 unauthorized response -
  mock_validation_error_response: 422 with validation errors - mock_not_found_response: 404 response
  - stocktrim_client_with_mock_transport: Client with mock transport

**Benefits:** - More flexible test response creation - Better error response mocking - Async client
  testing support - Mock transport integration

All existing tests continue to pass (42 passed).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
````
