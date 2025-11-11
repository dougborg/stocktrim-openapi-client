# ADR 0001: Parameter Flattening for MCP Tools

## Status

Accepted

## Context

When building MCP (Model Context Protocol) tools with FastMCP, we encountered issues
with parameter serialization when using nested Pydantic models as tool parameters.
Claude Code and other MCP clients had difficulty properly serializing and passing nested
object parameters to tools.

### The Problem

Our initial tool implementations used nested Pydantic models for parameter validation:

```python
class SearchProductsRequest(BaseModel):
    search_query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Max results")

async def search_products(
    request: SearchProductsRequest,
    context: Context
) -> SearchProductsResponse:
    # Implementation
```

This required MCP clients to pass a nested object:

```python
# What clients had to do (problematic):
await search_products(
    request={"search_query": "widget", "limit": 10},
    context=context
)
```

The nested object structure caused serialization issues in Claude Code and other MCP
clients, leading to failed tool calls and poor user experience.

### Business Impact

- Tool calls were failing due to parameter serialization errors
- Development velocity was slowed by debugging MCP protocol issues
- User experience was degraded when AI assistants couldn't reliably invoke tools

## Decision

We will use a parameter flattening decorator pattern to expose individual Pydantic model
fields as top-level tool parameters while maintaining the benefits of Pydantic
validation internally.

### Implementation

We adopted the `@unpack_pydantic_params` decorator pattern from the Katana MCP server
project:

1. **Created `unpack.py` module** - Provides the decorator and `Unpack` marker class
1. **Applied decorator to all tools** - 27 tools across 11 tool files
1. **Updated all tests** - Modified test files to use flattened parameters

The decorator transforms function signatures at import time using Python's introspection
APIs:

```python
from typing import Annotated
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

@unpack_pydantic_params
async def search_products(
    request: Annotated[SearchProductsRequest, Unpack()],
    context: Context
) -> SearchProductsResponse:
    # request is a validated SearchProductsRequest instance
    # but FastMCP sees individual parameters
```

This allows MCP clients to call tools with flattened parameters:

```python
# What clients can now do (working):
await search_products(
    search_query="widget",
    limit=10,
    context=context
)
```

### Technical Details

The `unpack_pydantic_params` decorator:

1. **Scans function signature** for `Annotated[Model, Unpack()]` parameters
1. **Extracts Pydantic fields** from the model class
1. **Creates new signature** with individual fields as `KEYWORD_ONLY` parameters
1. **Updates `__signature__` and `__annotations__`** so FastMCP sees flattened params
1. **At runtime**, reconstructs the Pydantic model from individual field values
1. **Passes validated model** to the original function

This provides:

- ✅ Flat parameters for MCP protocol compatibility
- ✅ Pydantic validation for type safety and business rules
- ✅ Clean tool implementation code (works with model instances)
- ✅ Automatic parameter documentation from Pydantic Field descriptions

## Consequences

### Positive

1. **Improved MCP Compatibility** - Tools work reliably with Claude Code and other MCP
   clients
1. **Maintained Type Safety** - Pydantic validation ensures parameter correctness
1. **Better Developer Experience** - Tool implementations work with typed model objects
1. **Consistent Pattern** - Single decorator applied uniformly across all tools
1. **Automatic Documentation** - Pydantic Field descriptions become parameter docs

### Negative

1. **Added Complexity** - Requires understanding of decorator pattern and signature
   introspection
1. **Import-time Magic** - Signature transformation happens at import, can be surprising
1. **Debugging Challenges** - Stack traces may show wrapper functions instead of
   original
1. **Pattern Learning Curve** - New developers need to understand
   `Annotated[Model, Unpack()]`

### Neutral

1. **Test Updates Required** - All tests must be updated to use flattened parameters
1. **Dependency on Python Introspection** - Relies on `inspect`, `typing`, and
   `get_type_hints()`
1. **Migration Effort** - Existing tools and tests needed updating (one-time cost)

## References

- **Katana MCP Implementation**:
  https://github.com/dougborg/katana-openapi-client/blob/main/katana_mcp_server/src/katana_mcp_server/unpack.py
- **Katana Implementation Commits**:
  - ef5980912bb2afa40b1b2d41a7c45639a33ba237 - Initial unpack implementation
  - 862ce79f10c244c3b711487cccbed7ccf744d27f - Test updates
  - a025ca98e0f8d279da03471800b7ebeb8da20ec7 - Documentation
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **MCP Protocol Specification**: https://modelcontextprotocol.io/

## Related Decisions

- Future ADR: Tool response model flattening (if needed)
- Future ADR: Error handling patterns for MCP tools

## Date

2025-11-10
