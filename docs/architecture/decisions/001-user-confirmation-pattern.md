# ADR 001: User Confirmation Pattern for Destructive Operations

**Status**: Accepted

**Date**: 2025-11-07

**Deciders**: Development Team

## Context and Problem Statement

The StockTrim MCP Server provides tools that perform destructive operations (deletions,
modifications) on production inventory data. Without user confirmation, AI agents could
accidentally:

- Delete critical inventory items, suppliers, or orders
- Modify forecast settings that impact business operations
- Make irreversible changes based on misinterpreted user intent

We need a standardized pattern for obtaining explicit user confirmation before executing
high-risk operations, while maintaining a good developer and user experience.

## Decision Drivers

- **Safety**: Prevent accidental data loss from AI agent errors or misinterpretation
- **User Experience**: Provide clear context about what will be deleted/modified
- **MCP Compliance**: Use native MCP protocol features rather than custom solutions
- **Developer Experience**: Easy to implement consistently across tools
- **Maintainability**: Pattern should be sustainable as we add more tools

## Considered Options

### Option 1: Pre-Flight Check (Tool Returns Preview)

Tools return a preview object requiring a second confirmation call.

**Pros**:

- Clear two-phase workflow
- Tool schema remains simple

**Cons**:

- Requires managing state between calls
- Two tool calls increases latency
- Complex for developers to implement consistently

### Option 2: Confirmation Parameter

Add `confirm: bool` parameter to destructive tools.

**Pros**:

- Simple implementation
- Single tool call

**Cons**:

- Defeats purpose - AI could set `confirm=true` automatically
- No preview of what will be deleted
- Not a real safety mechanism

### Option 3: Custom Prompt Pattern

Use tool description to instruct AI to confirm with user.

**Pros**:

- No code changes required
- Leverages AI capabilities

**Cons**:

- Unreliable - depends on AI following instructions
- No enforcement mechanism
- Inconsistent across different AI models

### Option 4: FastMCP Elicitation (MCP Native)

Use MCP's built-in elicitation protocol via FastMCP.

**Pros**:

- Native MCP feature with standardized protocol
- FastMCP provides clean Python API
- Forces human-in-the-loop confirmation
- Provides rich preview in confirmation message
- Widely adopted pattern in MCP ecosystem

**Cons**:

- Requires FastMCP v2.10.0+ (we already use v2.11.0)
- Slightly more complex than simple parameters

## Decision Outcome

**Chosen option**: **Option 4 - FastMCP Elicitation**

### Rationale

1. **MCP-Native Solution**: The MCP specification (2025-06-18) includes native
   elicitation support. Using the standard protocol ensures compatibility with all MCP
   clients.

1. **Industry Best Practice**: Analysis of production MCP servers (Git MCP, GitHub MCP,
   OpenAPI MCP) shows elicitation is the recommended pattern for destructive operations.

1. **Strong Safety Guarantees**: Unlike prompt-based or parameter-based approaches,
   elicitation provides a hard stop - the operation cannot proceed without explicit user
   approval.

1. **Rich Context**: Elicitation messages can include detailed previews (product names,
   costs, affected entities) helping users make informed decisions.

1. **Excellent DX**: FastMCP's `context.elicit()` API is simple and well-documented.
   Pattern matching on response types (`AcceptedElicitation`, `DeclinedElicitation`,
   `CancelledElicitation`) is clean and type-safe.

## Implementation Pattern

### Standard Elicitation Flow

```python
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

async def delete_entity(request: DeleteRequest, context: Context) -> DeleteResponse:
    """Delete an entity.

    🔴 HIGH-RISK OPERATION: This action permanently deletes data
    and cannot be undone. User confirmation is required via elicitation.
    """
    services = get_services(context)

    # 1. Fetch entity for preview
    entity = await services.get_by_code(request.code)

    if not entity:
        return DeleteResponse(success=False, message=f"Entity not found: {request.code}")

    # 2. Build rich preview message
    result = await context.elicit(
        message=f"""⚠️ Delete entity {entity.code}?

**{entity.name}**
Type: {entity.type}

This action will permanently delete the entity and cannot be undone.

Proceed with deletion?""",
        response_type=None,  # Simple yes/no approval
    )

    # 3. Handle elicitation response
    match result:
        case AcceptedElicitation():
            success, message = await services.delete(request.code)
            return DeleteResponse(
                success=success,
                message=f"✅ {message}" if success else message,
            )

        case DeclinedElicitation():
            return DeleteResponse(
                success=False,
                message=f"❌ Deletion of {entity.code} declined by user",
            )

        case CancelledElicitation():
            return DeleteResponse(
                success=False,
                message=f"❌ Deletion of {entity.code} cancelled by user",
            )

        case _:
            return DeleteResponse(
                success=False,
                message=f"Unexpected elicitation response for {entity.code}",
            )
```

### Tool Categorization

**HIGH-RISK (Require Elicitation)**:

- Deletions: `delete_product`, `delete_supplier`, `delete_purchase_order`,
  `delete_sales_orders`
- Irreversible modifications: TBD in Phase 2

**MEDIUM-RISK (Consider for Phase 2)**:

- Inventory modifications: `set_product_inventory`
- Forecast configuration: `update_forecast_settings`, `configure_product`
- Financial impact: `create_purchase_order` (large orders)

**LOW-RISK (No Elicitation Required)**:

- Read operations: All `get_*`, `list_*` tools
- Reversible creates: `create_product`, `create_supplier`

### Preview Message Guidelines

1. **Start with warning emoji**: `⚠️ Delete...?`
1. **Include entity details**: Name, code, status
1. **Show impact**: Associated data, financial amounts, affected records
1. **Use emoji indicators**: 🟢 Active, 🔴 Discontinued, 💰 Cost
1. **Clear consequences**: "This cannot be undone"
1. **Simple question**: "Proceed with deletion?"

### Response Message Guidelines

1. **Success**: Prefix with ✅ emoji
1. **Declined**: Prefix with ❌, include "declined by user"
1. **Cancelled**: Prefix with ❌, include "cancelled by user"
1. **Error**: No emoji, clear error message

### Testing Requirements

Each elicitation-protected tool must have tests for:

- ✓ Entity not found (skip elicitation)
- ✓ AcceptedElicitation (proceed with operation)
- ✓ DeclinedElicitation (abort, no operation performed)
- ✓ CancelledElicitation (abort, no operation performed)
- ✓ Preview message content (verify entity details shown)

## Consequences

### Positive

- **Improved Safety**: Eliminates accidental destructive operations
- **Better UX**: Users see exactly what will be deleted before confirming
- **Consistent Pattern**: All high-risk operations follow same flow
- **MCP Compliant**: Using standard protocol ensures broad client support
- **Auditable**: Elicitation responses can be logged for compliance

### Negative

- **Increased Latency**: Each destructive operation requires extra round-trip for
  confirmation
- **More Code**: Elicitation adds ~30 lines per tool compared to direct deletion
- **Testing Complexity**: Each tool needs 4-5 additional tests for elicitation paths

### Neutral

- **No Impact on Read Operations**: Only affects destructive tools
- **Backward Incompatible**: Old AI workflows expecting immediate deletion will break
  (this is intentional)

## Validation

### Success Criteria

- ✅ All 4 high-risk deletion tools implement elicitation (Phase 1)
- ✅ Comprehensive test coverage for elicitation responses
- ✅ Documentation updated with safety information
- ⏳ No accidental deletions in production (ongoing monitoring)

### Implementation Status

**Phase 1 (Completed)**:

- `delete_product` - Products tool
- `delete_supplier` - Suppliers tool
- `delete_purchase_order` - Purchase Orders tool
- `delete_sales_orders` - Sales Orders tool

**Phase 2 (Planned)**:

- Medium-risk modification tools (inventory, forecast)

**Phase 3 (Planned)**:

- Financial impact tools (large purchase orders)

## References

- [MCP Specification - Elicitation](https://spec.modelcontextprotocol.io/specification/2025-06-18/server/elicitation/)
- [FastMCP Documentation - Elicitation](https://github.com/jlowin/fastmcp)
- [Issue #80: Add user confirmation for destructive operations](https://github.com/dougborg/stocktrim-openapi-client/issues/80)
- ADR Template: [MADR 3.0.0](https://adr.github.io/madr/)

## Changelog

- 2025-11-07: Initial ADR documenting FastMCP Elicitation pattern
