# Safety Patterns in StockTrim MCP Server

This document describes the safety patterns and user confirmation mechanisms implemented
in the StockTrim MCP Server to prevent accidental data loss and ensure safe operation of
high-risk tools.

## Overview

The StockTrim MCP Server implements a **Human-in-the-Loop (HITL)** pattern for
operations that could result in permanent data loss or significant business impact. This
pattern uses the MCP protocol's native **elicitation** feature to request explicit user
confirmation before executing destructive operations.

## Risk Classification

All tools in the MCP server are classified by risk level to determine whether user
confirmation is required:

### 🔴 HIGH-RISK (Requires Confirmation)

Operations that permanently delete data and cannot be undone:

- `delete_product` - Permanently deletes a product from inventory
- `delete_supplier` - Permanently deletes a supplier and all associations (product
  mappings, purchase order history)
- `delete_purchase_order` - Permanently deletes a purchase order
- `delete_sales_orders` - Permanently deletes all sales orders for a product (bulk
  deletion)

**Pattern**: All HIGH-RISK operations require user confirmation via MCP elicitation with
detailed preview before execution.

### 🟡 MEDIUM-HIGH RISK (May Require Confirmation)

Operations that modify critical business data in ways that could cause operational
issues:

- `set_product_inventory` - Directly sets inventory levels (bypassing normal stock
  movements)
- `configure_product` - Changes product lifecycle/forecasting configuration
- `products_configure_lifecycle` - Bulk product lifecycle configuration changes
- `update_forecast_settings` - Changes global forecasting parameters

**Pattern**: May be implemented in Phase 2 with confirmation for bulk operations or
critical threshold changes.

### 🟠 MEDIUM RISK (Contextual Confirmation)

Operations that create financial obligations or commitments:

- `create_purchase_order` - Creates financial commitment to supplier
- `create_sales_order` - Creates customer order and inventory commitment
- `generate_purchase_orders_from_urgent_items` - Automated bulk PO generation

**Pattern**: May be implemented in Phase 3 with confirmation for high-value or bulk
operations.

### 🟢 LOW RISK (No Confirmation)

Reversible create operations:

- `create_product`, `create_supplier`, `create_customer`, `create_location`

**Pattern**: No confirmation required - these can be reversed by deleting the created
entity.

### ⚪ SAFE (No Confirmation)

Read-only operations:

- All `get_*`, `list_*`, `search_*`, `find_*` tools

**Pattern**: No confirmation required - read operations have no side effects.

## Elicitation Pattern

The MCP server uses FastMCP's elicitation API, which implements the MCP specification's
native confirmation protocol.

### Basic Flow

```python
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

async def high_risk_tool(request: Request, context: Context) -> Response:
    """High-risk tool with user confirmation."""

    # 1. Fetch entity details
    entity = await get_entity(request.id)
    if not entity:
        return Response(success=False, message="Entity not found")

    # 2. Build preview information
    preview = build_preview(entity)

    # 3. Request user confirmation
    result = await context.elicit(
        message=f"""⚠️ Delete {entity.name}?

{preview}

This action will permanently delete the data and cannot be undone.

Proceed with deletion?""",
        response_type=None,  # Simple yes/no approval
    )

    # 4. Handle elicitation response
    match result:
        case AcceptedElicitation():
            # User confirmed - proceed
            success, message = await delete_entity(entity.id)
            return Response(
                success=success,
                message=f"✅ {message}" if success else message,
            )

        case DeclinedElicitation():
            # User declined
            return Response(
                success=False,
                message=f"❌ Deletion declined by user",
            )

        case CancelledElicitation():
            # User cancelled
            return Response(
                success=False,
                message=f"❌ Deletion cancelled by user",
            )

        case _:
            # Unexpected response
            return Response(
                success=False,
                message="Unexpected elicitation response",
            )
```

### Preview Guidelines

The preview shown to the user should include:

1. **Entity Identification**: Code, name, or unique identifier
1. **Critical Context**: Status, relationships, financial impact
1. **Impact Warning**: Clear statement of what will be deleted/affected
1. **Irreversibility Notice**: Explicit statement that action cannot be undone

#### Example Previews

**Product Deletion**:

```
⚠️ Delete product WIDGET-001?

🟢 **Blue Widget**
Status: Active

This action will permanently delete the product and cannot be undone.

Proceed with deletion?
```

**Purchase Order Deletion**:

```
⚠️ Delete purchase order PO-2024-001?

**Supplier**: Acme Supplies (SUP-001)
**Status**: Draft
**Total Cost**: $1,550.00
**Line Items**: 3 items

This action will permanently delete the purchase order and cannot be undone.

Proceed with deletion?
```

**Bulk Sales Order Deletion**:

```
⚠️ Delete 15 sales orders for product WIDGET-001?

**Orders to Delete**: 15
**Total Quantity**: 450.0
**Customers Affected**: 8 customers
**Total Revenue**: $13,455.00

This action will permanently delete all sales orders for this product and cannot be undone.

Proceed with deletion?
```

### Response Handling

Always handle all three elicitation response types:

- **AcceptedElicitation**: User confirmed - proceed with operation
- **DeclinedElicitation**: User explicitly declined - abort operation
- **CancelledElicitation**: User cancelled prompt - abort operation

For success responses, prefix with ✅ emoji. For declined/cancelled responses, prefix
with ❌ emoji.

## Testing Elicitation

Elicitation behavior should be thoroughly tested:

```python
@pytest.mark.asyncio
async def test_delete_with_confirmation_accepted(mock_context, sample_entity):
    """Test deletion when user accepts confirmation."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.entity.get.return_value = sample_entity
    services.entity.delete.return_value = (True, "Entity deleted")
    mock_context.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))

    # Execute
    request = DeleteRequest(id="test-id")
    response = await delete_entity(request, mock_context)

    # Verify response
    assert response.success is True
    assert "✅" in response.message

    # Verify elicitation was called with preview
    mock_context.elicit.assert_called_once()
    elicit_args = mock_context.elicit.call_args
    assert "⚠️ Delete" in elicit_args[1]["message"]
    assert sample_entity.name in elicit_args[1]["message"]

    # Verify deletion was called
    services.entity.delete.assert_called_once_with("test-id")


@pytest.mark.asyncio
async def test_delete_with_confirmation_declined(mock_context, sample_entity):
    """Test deletion when user declines confirmation."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.entity.get.return_value = sample_entity
    mock_context.elicit = AsyncMock(return_value=DeclinedElicitation(data=None))

    # Execute
    request = DeleteRequest(id="test-id")
    response = await delete_entity(request, mock_context)

    # Verify response
    assert response.success is False
    assert "❌" in response.message
    assert "declined" in response.message

    # Verify deletion was NOT called
    services.entity.delete.assert_not_called()
```

Required test cases for each elicitation tool:

1. **Not Found**: Entity doesn't exist - no elicitation, early return
1. **Accepted**: User accepts - elicitation called, deletion proceeds
1. **Declined**: User declines - elicitation called, deletion aborted
1. **Cancelled**: User cancels - elicitation called, deletion aborted
1. **Preview Content**: Verify preview includes expected entity details

## Implementation Status

### Phase 1: HIGH-RISK Deletions ✅

All HIGH-RISK deletion operations now require user confirmation:

- ✅ `delete_product` -
  [products.py:214-296](../stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/products.py)
- ✅ `delete_supplier` -
  [suppliers.py:204-289](../stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/suppliers.py)
- ✅ `delete_purchase_order` -
  [purchase_orders.py:370-464](../stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/purchase_orders.py)
- ✅ `delete_sales_orders` -
  [sales_orders.py:290-404](../stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/sales_orders.py)

Test coverage: 20 tests added (5 per tool)

### Future Phases

**Phase 2: MEDIUM-HIGH RISK modifications** - Planned

- Confirmation for bulk inventory changes
- Confirmation for critical configuration changes

**Phase 3: MEDIUM RISK creates** - Planned

- Confirmation for high-value purchase orders
- Confirmation for bulk automated operations

## Best Practices

### For Tool Developers

1. **Always fetch entity first**: Get full entity details before elicitation to build
   accurate preview
1. **Build rich previews**: Include all relevant context (financial impact,
   relationships, status)
1. **Handle all response types**: Always handle Accepted, Declined, Cancelled, and
   unexpected responses
1. **Test thoroughly**: Write tests for all elicitation paths (not found, accepted,
   declined, cancelled, preview content)
1. **Document risk level**: Add 🔴 HIGH-RISK OPERATION notice to docstrings

### For MCP Clients

1. **Present elicitation UI**: Show elicitation message prominently with clear
   accept/decline options
1. **Preserve formatting**: Maintain markdown formatting and emoji in preview
1. **Allow cancellation**: Always provide a way for users to cancel/dismiss the prompt
1. **Log responses**: Record whether user accepted/declined for audit purposes

## Security Considerations

### Why Elicitation?

The MCP elicitation pattern provides stronger safety guarantees than alternatives:

- **Hard Stop**: Operation cannot proceed without explicit user approval
- **Protocol-Level**: Built into MCP specification, not application-level workaround
- **Client-Side UI**: Confirmation happens in user-facing client, not hidden in logs
- **Audit Trail**: Clients can log elicitation responses for compliance

### Defense in Depth

Elicitation is the first line of defense. Additional safeguards:

1. **API-Level Validation**: StockTrim API validates all operations
1. **Service Layer Checks**: Service methods validate business rules before API calls
1. **Database Constraints**: Foreign keys and constraints prevent invalid deletions
1. **Soft Deletes**: Consider implementing soft deletes in StockTrim API (future
   enhancement)

## References

- [MCP Specification - Elicitation](https://spec.modelcontextprotocol.io/specification/2025-06-18/server/elicitation/)
- [FastMCP Documentation - Elicitation](https://github.com/jlowin/fastmcp/tree/main/docs)
- [ADR 001: User Confirmation Pattern](../architecture/decisions/001-user-confirmation-pattern.md)
- [Issue #80: Add user confirmation for destructive operations](https://github.com/dougborg/stocktrim-openapi-client/issues/80)

## Support

For questions or issues with safety patterns:

1. Review [ADR 001](../architecture/decisions/001-user-confirmation-pattern.md) for
   architectural context
1. Check [tools.md](tools.md) for tool-specific documentation
1. Open an issue on GitHub for bugs or enhancement requests
