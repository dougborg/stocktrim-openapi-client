# ADR 003: Automated Tool Documentation Generation and Validation

**Status**: Proposed

**Date**: 2025-11-07

**Deciders**: Development Team

## Context and Problem Statement

The StockTrim MCP server currently has 40+ tools across foundation and workflow
categories. Each tool requires documentation in multiple places:

1. **Function docstrings** - Used by FastMCP to generate tool descriptions
1. **Pydantic Field descriptions** - Used for parameter documentation in JSON schemas
1. **Markdown documentation** - External documentation in
   [docs/mcp-server/tools.md](../../mcp-server/tools.md)

**Current Issues**:

- Documentation can drift out of sync between code and markdown
- No automated validation that field descriptions match docstring Args sections
- Risk indicators (🔴 HIGH-RISK) must be manually maintained in multiple places
- No enforcement of documentation standards (missing examples, incomplete Args sections)
- New tools may not follow established documentation patterns

We need a system to validate documentation consistency and potentially auto-generate
missing documentation.

## Decision Drivers

- **Consistency**: All tools should follow the same documentation patterns
- **Accuracy**: Code documentation and markdown docs should never drift apart
- **Developer Experience**: Easy to understand what documentation is required
- **Maintainability**: Changes to tool interfaces should automatically flag
  documentation updates
- **AI Integration**: Rich, accurate documentation helps AI agents use tools effectively
- **Safety**: Risk indicators must be consistently applied and validated

## Considered Options

### Option 1: Manual Documentation with Review Checklist

Continue current manual approach but add PR checklists.

**Pros**:

- No code changes required
- Maximum flexibility

**Cons**:

- Human error inevitable
- Review fatigue
- Documentation still drifts
- No enforcement mechanism

### Option 2: Runtime Introspection Only (Current State)

Rely entirely on FastMCP's runtime docstring extraction.

**Pros**:

- Already implemented
- Zero build-time overhead
- Simple developer experience

**Cons**:

- No validation of documentation quality
- No detection of missing descriptions
- Can't enforce standards
- Markdown docs separate from code

### Option 3: Build-Time Validation + Manual Documentation

Validate documentation at build time without auto-generation.

**Pros**:

- Catches documentation errors early
- Enforces standards
- Low implementation complexity
- Developers maintain control

**Cons**:

- Still requires manual doc updates
- Doesn't prevent drift, just detects it

### Option 4: Full Auto-Generation from Docstrings

Generate all documentation automatically from code.

**Pros**:

- Perfect synchronization
- No manual markdown maintenance
- Single source of truth

**Cons**:

- Loss of formatting flexibility
- Can't add editorial context
- Complex implementation
- Markdown loses richness

### Option 5: Hybrid: Validation + Selective Auto-Generation

Validate all documentation + auto-generate specific parts (parameter descriptions, risk
classifications).

**Pros**:

- Best of both worlds
- Enforces quality
- Reduces duplication
- Maintains editorial control
- Catches drift automatically

**Cons**:

- More complex than pure validation
- Requires tooling investment
- Learning curve for developers

## Decision Outcome

**Chosen option**: **Option 5 - Hybrid: Validation + Selective Auto-Generation**

### Rationale

1. **Validation First**: Build-time validation catches documentation issues before they
   reach production, preventing drift and enforcing standards.

1. **Selective Auto-Generation**: Generate repetitive, error-prone documentation (field
   descriptions from docstrings, risk classifications) while keeping editorial content
   (examples, use cases) manual.

1. **Developer Workflow**: Developers write docstrings once, validation ensures
   consistency, auto-generation eliminates duplication.

1. **Safety Critical**: Risk indicators (🔴 HIGH-RISK) can be auto-detected from
   elicitation usage and validated for consistency.

1. **Incremental Adoption**: Can be rolled out gradually - validation first, then
   auto-generation features.

## Implementation Plan

### Phase 1: Documentation Validation (Required for Merge)

**Goal**: Catch documentation inconsistencies at development time

**Components**:

1. **Docstring Parser** (`utils/docstring_parser.py`)

   - Parse Google-style docstrings
   - Extract: summary, Args section, Returns, Example JSON
   - Validate structure and completeness

1. **Tool Metadata Extractor** (`utils/tool_metadata.py`)

   - Extract tool information from function signatures
   - Detect risk level from elicitation usage
   - Build complete tool profile (name, params, risk, category)

1. **Validation Script** (`scripts/validate_tool_docs.py`)

   - Validate docstring completeness (all params documented)
   - Validate Field descriptions match Args section
   - Validate high-risk tools have 🔴 indicator
   - Validate example JSON is valid
   - Exit with error if validation fails

1. **Pre-commit Hook Integration**

   - Run validation on all modified tool files
   - Block commits with invalid documentation
   - Fast execution (< 1 second for changed files)

**Validation Rules**:

- ✅ All function parameters (except `context`) must have Args entries
- ✅ All Pydantic Field() must have description parameter
- ✅ Tools using `context.elicit()` must have 🔴 HIGH-RISK in docstring
- ✅ Example JSON (if present) must be valid and match request schema
- ✅ Response model must be documented in Returns section

### Phase 2: Parameter Description Auto-Generation (Optional Enhancement)

**Goal**: Reduce duplication between docstrings and Field descriptions

**Components**:

1. **Field Description Generator** (`utils/field_generator.py`)

   - Extract descriptions from docstring Args section
   - Generate/update Pydantic Field(description=...) statements
   - Preserve manual descriptions that add value beyond Args

1. **Generation CLI** (`scripts/generate_field_docs.py`)

   - Scan all tools for missing Field descriptions
   - Propose auto-generated descriptions from docstrings
   - Interactive mode: review and approve changes
   - Batch mode: auto-apply for CI/CD

**Usage**:

```bash
# Interactive mode - review each change
uv run poe generate-field-docs

# Batch mode - auto-apply all
uv run poe generate-field-docs --auto-approve

# Check what would change
uv run poe generate-field-docs --dry-run
```

### Phase 3: Markdown Documentation Sync (Future)

**Goal**: Keep code and markdown docs synchronized

**Components**:

1. **Markdown Generator** (`scripts/generate_tool_docs_md.py`)

   - Extract all tool metadata from code
   - Generate markdown sections for tools.md
   - Preserve hand-written sections (How It Works, Use Cases)
   - Update parameter tables automatically

1. **Documentation Index** (JSON artifact)

   - Export tool metadata to `docs/tool-index.json`
   - Used by documentation site
   - Used by CI to detect changes

**Output**: Updated `docs/mcp-server/tools.md` with:

- Auto-generated parameter tables
- Risk indicators
- Tool signatures
- Manual sections preserved (## How It Works, ## Use Cases)

## Implementation Pattern

### Validation Example

```python
# scripts/validate_tool_docs.py
from stocktrim_mcp_server.utils.docstring_parser import DocstringParser
from stocktrim_mcp_server.utils.tool_metadata import ToolMetadataExtractor

def validate_tool(tool_function) -> list[str]:
    """Validate a tool's documentation.

    Returns list of validation errors (empty if valid).
    """
    errors = []
    parser = DocstringParser.from_function(tool_function)
    extractor = ToolMetadataExtractor(tool_function)

    # Rule 1: All parameters must be documented
    for param in extractor.parameters:
        if param.name not in parser.args and param.name != 'context':
            errors.append(f"Parameter '{param.name}' missing from Args section")

    # Rule 2: High-risk tools must have indicator
    if extractor.uses_elicitation and '🔴' not in parser.summary:
        errors.append("Tool uses elicitation but missing 🔴 HIGH-RISK indicator")

    # Rule 3: Field descriptions required
    if extractor.request_model:
        for field_name, field_info in extractor.request_model.__fields__.items():
            if not field_info.description:
                errors.append(f"Field '{field_name}' missing description")

    return errors
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-tool-docs
        name: Validate Tool Documentation
        entry: uv run python scripts/validate_tool_docs.py
        language: system
        files: stocktrim_mcp_server/src/stocktrim_mcp_server/tools/.*\.py$
        pass_filenames: true
```

### Auto-Generation Example

```python
# scripts/generate_field_docs.py
from stocktrim_mcp_server.utils.docstring_parser import DocstringParser
import ast

def generate_field_descriptions(tool_file_path: str) -> dict[str, str]:
    """Extract field descriptions from docstring Args section.

    Returns mapping of field_name -> description.
    """
    # Parse Python file
    with open(tool_file_path) as f:
        tree = ast.parse(f.read())

    # Find tool function
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            # Extract docstring
            parser = DocstringParser(ast.get_docstring(node) or "")

            # Find request model class
            for param in node.args.args:
                if param.arg.endswith('Request'):
                    # Found request model, generate Field descriptions
                    return parser.args

    return {}
```

## Documentation Standards

### Required Docstring Structure

```python
async def tool_name(request: ToolRequest, context: Context) -> ToolResponse:
    """[REQUIRED] One-line summary. [OPTIONAL] 🔴 HIGH-RISK for elicitation tools.

    [OPTIONAL] Extended description explaining what the tool does,
    when to use it, and any important notes.

    Args:
        request: [REQUIRED] Description of request parameter
        context: [AUTO-IGNORED] Server context (not documented)

    Returns:
        [REQUIRED] Description of return value

    Example:
        [REQUIRED for workflow tools, OPTIONAL for foundation tools]
        Request: {"field": "value"}
        Returns: {"success": true, "message": "Done"}

    [WORKFLOW TOOLS ONLY]
    ## How It Works

    Explanation of tool's algorithm or process.

    ## Common Use Cases

    When to use this tool.

    ## See Also

    - `related_tool_1`: Description
    - `related_tool_2`: Description
    """
```

### Required Field Structure

```python
class ToolRequest(BaseModel):
    """[REQUIRED] Brief description of request model."""

    required_field: str = Field(
        ...,
        description="[REQUIRED] What this field represents"
    )
    optional_field: int | None = Field(
        default=None,
        description="[REQUIRED] What this optional field represents"
    )
```

### Risk Indicator Requirements

**HIGH-RISK** (🔴):

- Tools using `context.elicit()`
- Irreversible data modifications
- Financial impact operations

**MEDIUM-RISK** (🟡) - Future:

- Inventory modifications
- Configuration changes
- Bulk operations

**LOW-RISK** (🟢):

- Read-only operations
- Reversible creates

## Consequences

### Positive

- **Consistency Enforcement**: All tools follow same documentation patterns
- **Early Error Detection**: Documentation errors caught before merge
- **Reduced Duplication**: Field descriptions auto-generated from docstrings
- **Safety Validation**: High-risk tools automatically validated for risk indicators
- **Better AI Integration**: Consistent, complete documentation helps AI agents
- **Developer Guidance**: Clear standards and automated feedback

### Negative

- **Build Time Increase**: Validation adds ~1-2 seconds to pre-commit
- **Learning Curve**: Developers must understand documentation standards
- **Tooling Maintenance**: Validation and generation scripts need maintenance
- **Initial Migration**: Existing tools may need documentation updates

### Neutral

- **Documentation Still Required**: Auto-generation doesn't eliminate writing docs
- **Editorial Control Preserved**: Manual sections like "How It Works" still
  hand-written

## Validation

### Success Criteria

- ✅ All 40+ tools pass documentation validation
- ✅ Pre-commit hook catches missing documentation
- ✅ Zero drift between Field descriptions and Args sections
- ✅ All high-risk tools have 🔴 indicator
- ✅ All example JSON is valid

### Metrics

- **Validation Coverage**: % of tools with complete documentation
- **Validation Speed**: Pre-commit validation time < 2 seconds
- **Auto-Generation Accuracy**: % of generated descriptions that don't need manual
  editing

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Pydantic Field Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [FastMCP Tool Registration](https://github.com/jlowin/fastmcp)
- ADR 001: User Confirmation Pattern (risk classification)
- ADR 002: Tool Interface Pattern (Pydantic models)
- Investigation: `TOOL_DOCUMENTATION_INVESTIGATION.md`
- Implementation Guide: `autogen_implementation_guide.md`

## Changelog

- 2025-11-07: Initial ADR proposing validation + selective auto-generation approach
