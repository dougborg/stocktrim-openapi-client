# ADR 002: Tool Interface Pattern with Pydantic Models

**Status**: Accepted

**Date**: 2025-11-07

**Deciders**: Development Team

## Context and Problem Statement

MCP tools need well-defined interfaces that:

- Provide type safety and validation
- Generate accurate JSON schemas for AI agents
- Offer clear documentation through field descriptions
- Enable IDE autocomplete and type checking
- Maintain consistency across all tools

We need a pattern that transforms Python type hints into MCP tool schemas while
providing robust validation and excellent developer experience.

## Decision Drivers

- **Type Safety**: Catch interface errors at development time, not runtime
- **Schema Generation**: Automatically generate accurate JSON schemas for MCP protocol
- **Documentation**: Field descriptions should flow through to AI agents
- **Validation**: Input validation should happen before business logic
- **Developer Experience**: Pattern should be easy to understand and implement
- **Maintainability**: Changes to interfaces should be centralized and obvious

## Considered Options

### Option 1: Plain Function Parameters

Use standard Python function parameters directly.

```python
async def delete_product(
    context: Context,
    product_code: str
) -> dict:
    ...
```

**Pros**:

- Simple and familiar
- No additional dependencies

**Cons**:

- No automatic schema generation
- Manual validation required
- Field descriptions buried in docstrings
- No complex nested structures
- Hard to generate documentation

### Option 2: TypedDict with Manual Schema

Use TypedDict for typing, manually define JSON schema.

```python
class DeleteProductParams(TypedDict):
    product_code: str

SCHEMA = {...}  # Manual JSON schema

async def delete_product(context: Context, params: DeleteProductParams) -> dict:
    ...
```

**Pros**:

- Type hints available
- Control over schema

**Cons**:

- Duplicate definitions (TypedDict + schema)
- Easy to get out of sync
- No automatic validation
- More boilerplate

### Option 3: Pydantic Models with FastMCP Integration

Use Pydantic v2 models for request/response, FastMCP `mcp.tool()` decorator for
registration.

```python
class DeleteProductRequest(BaseModel):
    """Request model for deleting a product."""

    product_code: str = Field(..., description="Product code to delete")

class DeleteProductResponse(BaseModel):
    """Response from delete operation."""

    success: bool
    message: str

async def delete_product(
    request: DeleteProductRequest,
    context: Context
) -> DeleteProductResponse:
    """Delete a product by code.

    🔴 HIGH-RISK OPERATION: This action permanently deletes product data
    and cannot be undone. User confirmation is required via elicitation.
    """
    ...

def register_tools(mcp: FastMCP) -> None:
    mcp.tool()(delete_product)
```

**Pros**:

- Automatic JSON schema generation from Pydantic models
- Built-in validation with clear error messages
- Field descriptions become part of schema
- Type safety throughout the stack
- FastMCP handles model ↔ JSON conversion
- Supports complex nested structures
- Excellent IDE support
- Single source of truth for interface

**Cons**:

- Requires Pydantic dependency (already used)
- Slightly more verbose than plain functions
- Learning curve for Pydantic patterns

## Decision Outcome

**Chosen option**: **Option 3 - Pydantic Models with FastMCP Integration**

### Rationale

1. **Automatic Schema Generation**: FastMCP's `mcp.tool()` decorator automatically
   extracts JSON schemas from Pydantic models, eliminating manual schema definitions and
   ensuring they never drift out of sync.

1. **Validation at Boundary**: Pydantic validates all inputs before they reach business
   logic, converting validation errors into clear MCP error responses.

1. **Self-Documenting**: Field descriptions in `Field()` definitions automatically
   appear in the generated schema, providing context to AI agents.

1. **Type Safety**: Full type checking from client input through to service layer calls.

1. **Industry Standard**: Pydantic is the de facto standard for data validation in
   Python APIs, with extensive tooling and community support.

## Implementation Pattern

### Standard Tool Structure

```python
from pydantic import BaseModel, Field
from fastmcp import FastMCP, Context

# 1. Define Request Model
class ToolRequest(BaseModel):
    """Brief description of what this request does."""

    required_field: str = Field(
        ...,
        description="What this field represents"
    )
    optional_field: int | None = Field(
        default=None,
        description="What this optional field represents"
    )

# 2. Define Response Model
class ToolResponse(BaseModel):
    """Response from the tool."""

    success: bool
    message: str
    data: dict | None = None

# 3. Implement Tool Function
async def tool_name(
    request: ToolRequest,
    context: Context
) -> ToolResponse:
    """Tool description that appears in MCP.

    Longer explanation of what the tool does.
    Include usage examples and important notes.

    Args:
        request: Request parameters
        context: Server context with services

    Returns:
        ToolResponse indicating result

    Example:
        Request: {"required_field": "value"}
        Returns: {"success": true, "message": "Done"}
    """
    services = get_services(context)
    # ... implementation ...
    return ToolResponse(success=True, message="Success")

# 4. Register Tool
def register_tools(mcp: FastMCP) -> None:
    """Register tools with FastMCP server."""
    mcp.tool()(tool_name)
```

### Model Naming Conventions

- **Request models**: `{ToolName}Request` - e.g., `DeleteProductRequest`
- **Response models**: `{ToolName}Response` - e.g., `DeleteProductResponse`
- **Nested data models**: `{EntityName}Info` or `{EntityName}Data` - e.g.,
  `ProductInfo`, `LineItemRequest`

### Field Definition Guidelines

1. **Always include descriptions**: Every field should have a `description` parameter
1. **Use Field() for configuration**: Constraints, defaults, examples all go in
   `Field()`
1. **Validation in model**: Use Pydantic validators for complex validation logic
1. **Optional vs required**: Use `| None` with `default=None` for optional fields
1. **Docstrings on models**: Provide class-level documentation for the model's purpose

### FastMCP Integration Pattern

1. **Context parameter**: Always accept `context: Context` as second parameter
1. **Type hints required**: FastMCP needs typed parameters to generate schema
1. **Decorator registration**: Use `mcp.tool()(function_name)` pattern
1. **Automatic conversion**: FastMCP handles JSON ↔ Pydantic conversion

### Validation Behavior

```python
class CreateProductRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    cost: float = Field(..., gt=0)  # Greater than 0
    quantity: int = Field(default=0, ge=0)  # Greater than or equal to 0
```

If invalid data is sent:

- FastMCP catches Pydantic validation error
- Returns MCP error with validation details
- Tool function never executes
- No business logic contamination

### Complex Nested Structures

```python
class LineItemRequest(BaseModel):
    """Line item for purchase order."""

    product_code: str = Field(..., description="Product code")
    quantity: float = Field(..., description="Quantity to order", gt=0)
    unit_price: float | None = Field(default=None, description="Unit price")

class CreatePurchaseOrderRequest(BaseModel):
    """Request model for creating a purchase order."""

    supplier_code: str = Field(..., description="Supplier code")
    line_items: list[LineItemRequest] = Field(
        ...,
        description="Line items for the purchase order",
        min_length=1
    )
```

FastMCP automatically generates nested schemas for `LineItemRequest` within the parent
schema.

## Consequences

### Positive

- **Zero Schema Drift**: Models and schemas are always in sync
- **Early Validation**: Invalid inputs caught before reaching business logic
- **Better AI Integration**: Rich schemas help AI agents understand tool capabilities
- **Type Safety**: Full typing from MCP boundary through to database
- **Documentation**: Field descriptions serve dual purpose (code docs + AI context)
- **Refactoring Safety**: Type errors caught at development time

### Negative

- **More Boilerplate**: Each tool needs 2-3 model classes (Request, Response, nested)
- **Learning Curve**: Developers need to understand Pydantic patterns
- **Import Overhead**: Each tool file imports BaseModel, Field, etc.

### Neutral

- **Pydantic Dependency**: Already used throughout codebase, not additional
- **Model Classes**: Some developers prefer plain functions, but models provide
  structure

## Validation

### Success Criteria

- ✅ All 40+ tools use Pydantic request/response models
- ✅ All fields have description strings
- ✅ JSON schemas automatically generated by FastMCP
- ✅ Validation errors return clear MCP error responses
- ✅ No manual JSON schema definitions in codebase

### Current Implementation Status

**Compliant Tools** (All current tools):

- Foundation tools: Products, Customers, Suppliers, Locations, Inventory, Purchase
  Orders, Sales Orders
- Workflow tools: Forecast Management, Urgent Orders, Product Management

**Pattern Variations**:

- Some response models use dict instead of Pydantic (acceptable for dynamic data)
- Some tools use `pass` for empty request models (acceptable for list operations)

## References

- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [FastMCP Tool Registration](https://github.com/jlowin/fastmcp)
- [MCP Specification - Tool Schema](https://spec.modelcontextprotocol.io/specification/2025-06-18/server/tools/)
- [Pydantic Field Types](https://docs.pydantic.dev/latest/concepts/fields/)
- ADR 001: User Confirmation Pattern (uses this interface pattern)

## Changelog

- 2025-11-07: Initial ADR documenting Pydantic + FastMCP tool interface pattern
