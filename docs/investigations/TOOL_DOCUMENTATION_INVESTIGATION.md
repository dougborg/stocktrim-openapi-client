# StockTrim MCP Server - Tool Documentation Investigation

This directory contains a complete investigation into how tool descriptions are
documented in the StockTrim MCP server and explores auto-generation possibilities.

## Documents Included

### 1. tool_documentation_analysis.md (722 lines)

Comprehensive analysis of the current tool documentation patterns:

**Contents:**

- Current Documentation Pattern (tool registration, docstrings, Pydantic Field
  descriptions)
- Tool Signature Analysis (consistent async function pattern, request/response models)
- FastMCP Integration (how it extracts docstrings, what it supports)
- Auto-generation Possibilities (low/medium/advanced effort opportunities)
- Existing Utilities and Tools (what FastMCP provides)
- Documentation Examples (foundation vs workflow tools)
- Recommendations for implementation

**Key Sections:**

- Section 1: Current Documentation Pattern (4.1 KB)
- Section 2: Tool Signature Analysis (3.2 KB)
- Section 3: FastMCP Integration (4.8 KB)
- Section 4: Auto-generation Possibilities (5.1 KB)
- Section 5: Existing Utilities (2.9 KB)
- Section 6: Documentation Examples (8.3 KB)
- Section 7: Recommendations (2.1 KB)
- Appendix: File Locations (1.5 KB)

### 2. autogen_implementation_guide.md (764 lines)

Production-ready code examples for implementing auto-generation utilities:

**Contents:**

- 6 Complete Implementations (~850 lines of code):
  1. Docstring Parser Utility (220 lines)
  1. Tool Metadata Extractor (280 lines)
  1. Field Description Auto-Generator (60 lines)
  1. Tool Registration Metadata Hook (80 lines)
  1. Test Suite (120 lines)
  1. Build Integration Script (90 lines)

**Key Components:**

- DocstringParser: Extracts documentation from Google-style docstrings
- ToolMetadataExtractor: Builds complete tool profiles with risk detection
- ToolMetadataCollector: Collects from all tools, exports JSON/Markdown
- Generate Tool Docs script: CI/CD integration for auto-generation

## Investigation Summary

### Current Findings

The StockTrim MCP server uses a **manual documentation pattern** where:

1. **Tool Descriptions** come from function docstrings

   - FastMCP extracts via `inspect.getdoc()` automatically
   - Docstrings follow Google-style format with Args/Returns/Examples

1. **Parameter Documentation** is in Pydantic `Field(description=...)`

   - Manually maintained in request model definitions
   - FastMCP converts to JSON schema automatically

1. **Workflow Tools** use extended Markdown documentation

   - Sections: "## How It Works", "## Common Use Cases", "## Typical Workflow"
   - Cross-references with "## See Also"

1. **High-Risk Operations** are marked with emoji

   - 🔴 HIGH-RISK for destructive operations (delete)
   - User confirmation required via elicitation protocol

### Key FastMCP Integration Points

- **Tool.from_function()** at line 248 of fastmcp/tools/tool.py
- **ParsedFunction.from_function()** at line 265 extracts metadata
- **inspect.getdoc()** at line 403 extracts docstring
- **Pydantic Field()** descriptions automatically included in schema

### Auto-Generation Opportunities

**LOW EFFORT (Easy to implement):**

1. Parse docstrings to extract parameter descriptions
1. Auto-populate Field(description=...) from Args section
1. Extract and validate Example JSON

**MEDIUM EFFORT (Requires infrastructure):**

1. Auto-detect tool category (foundation vs workflow)
1. Auto-classify risk levels based on keywords
1. Generate markdown documentation
1. Build tool categorization system

**ADVANCED (Major changes):**

1. Enforce docstring templates
1. Generate docstrings from function signatures
1. LLM-assisted documentation

## File Structure

### Tool Modules

```
stocktrim_mcp_server/src/stocktrim_mcp_server/tools/
├── foundation/          # CRUD tools
│   ├── customers.py
│   ├── products.py
│   ├── suppliers.py
│   ├── locations.py
│   ├── inventory.py
│   ├── purchase_orders.py
│   └── sales_orders.py
├── workflows/           # High-level operations
│   ├── urgent_orders.py
│   ├── forecast_management.py
│   └── product_management.py
├── __init__.py
├── foundation/__init__.py
└── workflows/__init__.py
```

### Key File Locations

**Documentation Source:**

- Tool implementations:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/*.py`
- Workflow tools: `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/workflows/*.py`
- Tool reference: `docs/mcp-server/tools.md`

**FastMCP Source:**

- Tool processing: `.venv/lib/python3.13/site-packages/fastmcp/tools/tool.py`
- ParsedFunction class: line 360
- Docstring extraction: line 403

## Quick Reference

### Current Tool Pattern

All tools follow this consistent pattern:

```python
async def <tool_name>(
    request: <RequestModel>,
    context: Context
) -> <ResponseType>:
    """<One-line summary>.

    <Detailed description>

    Args:
        request: Request containing ...
        context: Server context with StockTrimClient

    Returns:
        <Return type description>

    Example:
        Request: {...}
        Returns: {...}
    """
```

### Request Model Pattern

```python
class GetProductRequest(BaseModel):
    """Request model for getting a product."""
    code: str = Field(..., description="Product code to retrieve")
    category: str | None = Field(
        default=None, description="Optional category filter"
    )
```

### Response Model Pattern

```python
class ProductInfo(BaseModel):
    """Product information."""
    code: str
    name: str | None
    is_active: bool
    price: float | None
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2, Low effort)

- Create DocstringParser utility
- Create ToolMetadataExtractor
- Add extraction tests
- Validate on all existing tools

### Phase 2: Auto-generation (Weeks 3-4, Medium effort)

- Implement markdown documentation generator
- Add risk classification system
- Build tool categorization
- Integrate into documentation build

### Phase 3: Enforcement (Week 5+, Advanced)

- Define docstring template standard
- Add pre-commit hook validation
- Integrate with CI/CD pipeline
- Explore LLM-assisted updates

## Usage Examples

### Extract Tool Metadata

```python
from utils.tool_metadata import ToolMetadataExtractor
from tools.foundation.customers import get_customer

extractor = ToolMetadataExtractor(get_customer)
metadata = extractor.extract()

print(metadata.name)        # "get_customer"
print(metadata.category)    # "foundation"
print(metadata.risk_level)  # "low"
print(metadata.parameters)  # List of ParameterMetadata
```

### Generate Documentation

```python
from utils.tool_metadata import ToolMetadataCollector

collector = ToolMetadataCollector("stocktrim_mcp_server/tools")
# ... collect from all modules ...

# Generate markdown
with open("docs/tools_generated.md", "w") as f:
    f.write(collector.to_markdown())

# Export JSON
with open("docs/tools_metadata.json", "w") as f:
    f.write(collector.to_json())
```

## Key Statistics

- **Total Tools**: 20+
- **Foundation Tools**: 15+ (CRUD operations)
- **Workflow Tools**: 5+ (High-level operations)
- **Request Models**: 1 per tool
- **Response Models**: 1 per tool
- **Lines to implement auto-gen**: ~850 lines

## Recommendations

1. **Start with Phase 1** - Low effort, validates approach
1. **Focus on single source of truth** - Docstrings as primary documentation
1. **Automate what can be automated** - Risk levels, categories, basic descriptions
1. **Keep manual content where it adds value** - Extended workflow documentation,
   examples
1. **Integrate into CI/CD early** - Prevents documentation drift

## Related Documentation

- Server Implementation: `docs/mcp-server/overview.md`
- Tool Reference: `docs/mcp-server/tools.md`
- Examples: `docs/mcp-server/examples.md`
- Safety Patterns: `docs/mcp-server/safety-patterns.md`

## Contact & Questions

For questions about this investigation or the implementation approach, refer to:

- The detailed analysis in `tool_documentation_analysis.md`
- The code examples in `autogen_implementation_guide.md`
- The tool source files in `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/`
