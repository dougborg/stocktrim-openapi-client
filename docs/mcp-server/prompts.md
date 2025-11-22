# MCP Prompts

The StockTrim MCP Server provides workflow prompts that guide AI agents through complex
multi-step inventory management tasks. Prompts combine system instructions with user
parameters to create comprehensive task templates.

## What are MCP Prompts?

MCP Prompts are pre-configured templates that:

- Provide structured guidance for complex workflows
- Combine multiple tool calls into coherent processes
- Include domain expertise and best practices
- Reduce the need for users to understand implementation details

Unlike tools (which perform specific actions), prompts provide high-level workflow
guidance that the AI agent executes using available tools and resources.

## Available Prompts

The MCP server provides **5 workflow prompts** for guided inventory management:

1. **purchasing_workflow** - Comprehensive purchasing review and order generation
1. **forecast_accuracy_review** - Analyze and improve forecast accuracy
1. **supplier_performance_review** - Comprehensive supplier analysis
1. **stockout_prevention** - Proactive inventory management and reordering
1. **product_lifecycle_review** - Product performance and lifecycle analysis

### Purchasing Workflow

**Name:** `purchasing_workflow`

**Description:** Comprehensive purchasing review and purchase order generation workflow.

**Purpose:** Guides the AI through analyzing reorder requirements, grouping products by
supplier, generating purchase orders, and providing cost analysis with recommendations.

**Expected Duration:** 3-5 minutes

#### Parameters

| Parameter        | Type | Required | Default | Description                                   |
| ---------------- | ---- | -------- | ------- | --------------------------------------------- |
| `location_code`  | str  | Yes      | -       | Location code to review (e.g., 'WAREHOUSE-A') |
| `days_threshold` | int  | No       | 30      | Days of stock threshold for urgency           |

#### Workflow Steps

The prompt guides the AI through a structured 4-step process:

**Step 1: Analyze Requirements**

- Use `review_urgent_order_requirements` tool with the specified threshold
- Review `stocktrim://reports/urgent-orders` resource for context
- Identify products needing reorder
- Flag critical items (< 7 days stock)

**Step 2: Group by Supplier**

- Organize products by supplier for efficient ordering
- Calculate total units and costs per supplier
- Check `stocktrim://reports/supplier-directory` for supplier details
- Identify minimum order requirements

**Step 3: Generate Purchase Orders**

- Use `generate_purchase_orders_from_urgent_items` for each supplier
- Prioritize suppliers with critical items
- Review generated PO details
- Flag issues (inactive suppliers, cost anomalies)

**Step 4: Summary and Recommendations**

- Provide executive summary
- Report total products ordered across all POs
- Detail total cost by supplier and overall
- Estimate delivery timelines
- Flag items requiring special approval
- Offer budget considerations

#### Tools Used

- `review_urgent_order_requirements`: Analyze what needs to be ordered
- `generate_purchase_orders_from_urgent_items`: Create draft POs for urgent items

#### Resources Referenced

- `stocktrim://reports/urgent-orders`: Current urgent order requirements
- `stocktrim://reports/supplier-directory`: Supplier contact information
- `stocktrim://products/{code}`: Individual product details
- `stocktrim://suppliers/{code}`: Individual supplier details

#### Output Format

The AI provides a structured markdown report with:

1. **Executive Summary** (2-3 sentences)
1. **Critical Items Section** (< 7 days stock)
1. **Standard Items Section** (7-threshold days stock)
1. **Generated Purchase Orders** (one section per supplier)
1. **Cost Analysis** (table format)
1. **Recommendations** (bulleted list)
1. **Approval Checklist**

#### Example Usage

**In Claude Desktop:**

```
Use the purchasing_workflow prompt with location_code="WAREHOUSE-A" and days_threshold=30
```

**Via MCP Inspector:**

```json
{
  "name": "purchasing_workflow",
  "arguments": {
    "location_code": "WAREHOUSE-A",
    "days_threshold": 30
  }
}
```

#### Best Practices

- **Use realistic thresholds**: 7 days for critical, 30 days for standard planning
- **Review before approval**: POs are drafts - review in StockTrim UI before final
  approval
- **Check supplier status**: Ensure suppliers are active before generating orders
- **Budget awareness**: Monitor cost anomalies and get approval for high-cost items
- **Prioritize critical items**: Items < 7 days stock should be ordered first

#### When to Use

Use the purchasing workflow when you need to:

- Conduct regular reorder reviews
- Process urgent stockout situations
- Generate bulk purchase orders efficiently
- Get structured cost analysis and recommendations
- Ensure nothing critical is missed in reorder process

### Forecast Accuracy Review

**Name:** `forecast_accuracy_review`

**Description:** Analyze forecast accuracy, identify patterns, and optimize forecast
settings for improved planning.

**Purpose:** Guides the AI through reviewing historical forecast accuracy, identifying
systematic errors or patterns, and recommending adjustments to forecast parameters.

**Expected Duration:** 2-4 minutes

#### Parameters

| Parameter       | Type | Required | Default | Description                                     |
| --------------- | ---- | -------- | ------- | ----------------------------------------------- |
| `location_code` | str  | No       | None    | Location to analyze (if None, reviews all)      |
| `lookback_days` | int  | No       | 90      | Historical period to analyze (default: 90 days) |

#### Workflow Steps

The prompt guides the AI through analyzing forecast accuracy:

**Step 1: Historical Analysis**

- Review actual vs. forecasted demand over the lookback period
- Identify products with significant forecast errors
- Calculate accuracy metrics (MAPE, bias, etc.)

**Step 2: Pattern Identification**

- Identify systematic over-forecasting or under-forecasting
- Detect seasonal patterns not captured by forecasts
- Flag products with high volatility

**Step 3: Parameter Optimization**

- Recommend adjustments to lead times
- Suggest safety stock changes
- Identify products needing manual review

**Step 4: Recommendations**

- Provide actionable steps to improve forecast accuracy
- Prioritize high-impact changes
- Document expected improvements

#### When to Use

Use the forecast accuracy review when you need to:

- Conduct regular forecast performance reviews
- Investigate why forecasts are consistently off
- Optimize inventory planning parameters
- Identify products needing special attention

### Supplier Performance Review

**Name:** `supplier_performance_review`

**Description:** Comprehensive supplier performance review and analysis.

**Purpose:** Guides the AI through evaluating supplier reliability, cost
competitiveness, and delivery performance over time.

**Expected Duration:** 2-4 minutes

#### Parameters

| Parameter       | Type | Required | Default | Description                                        |
| --------------- | ---- | -------- | ------- | -------------------------------------------------- |
| `supplier_code` | str  | No       | None    | Specific supplier to review (if None, reviews all) |
| `period_days`   | int  | No       | 90      | Historical period to analyze (default: 90 days)    |

#### Workflow Steps

The prompt guides the AI through supplier analysis:

**Step 1: Performance Metrics**

- Analyze on-time delivery rates
- Review order fulfillment accuracy
- Calculate average lead times

**Step 2: Cost Analysis**

- Compare costs across suppliers for common products
- Identify cost trends over time
- Flag pricing anomalies

**Step 3: Relationship Health**

- Review order frequency and volumes
- Identify concentration risks
- Assess supplier dependency

**Step 4: Recommendations**

- Suggest supplier consolidation or diversification
- Recommend price renegotiations
- Flag suppliers needing attention

#### When to Use

Use the supplier performance review when you need to:

- Conduct regular supplier evaluations
- Compare multiple suppliers for strategic decisions
- Identify underperforming suppliers
- Support contract renewal discussions

### Stockout Prevention

**Name:** `stockout_prevention`

**Description:** Proactive stockout prevention workflow: analyze inventory levels,
identify gaps, and create preventive purchase orders.

**Purpose:** Guides the AI through identifying potential stockouts before they occur and
taking preventive action.

**Expected Duration:** 2-3 minutes

#### Parameters

| Parameter       | Type | Required | Default | Description                               |
| --------------- | ---- | -------- | ------- | ----------------------------------------- |
| `location_code` | str  | Yes      | -       | Location code to analyze                  |
| `days_ahead`    | int  | No       | 14      | Days ahead to forecast (default: 14 days) |

#### Workflow Steps

The prompt guides the AI through proactive prevention:

**Step 1: Risk Identification**

- Analyze current inventory levels vs. forecasted demand
- Identify products at risk of stockout within the forecast window
- Calculate days until stockout for each product

**Step 2: Priority Assessment**

- Rank products by stockout risk and business impact
- Consider lead times and minimum order quantities
- Flag critical items needing immediate attention

**Step 3: Preventive Action**

- Generate purchase orders for at-risk items
- Suggest safety stock adjustments
- Recommend expedited shipping if needed

**Step 4: Monitoring Plan**

- Set up alerts for high-risk items
- Recommend follow-up review dates
- Document action items

#### When to Use

Use the stockout prevention workflow when you need to:

- Proactively avoid stockouts before they happen
- Plan ahead for seasonal demand increases
- Monitor critical items with tight inventory levels
- Reduce emergency ordering and expediting costs

### Product Lifecycle Review

**Name:** `product_lifecycle_review`

**Description:** Product performance and lifecycle analysis.

**Purpose:** Guides the AI through evaluating product performance, identifying
slow-moving or obsolete items, and making lifecycle decisions.

**Expected Duration:** 2-4 minutes

#### Parameters

Product lifecycle review parameters are defined dynamically based on the analysis scope.

#### Workflow Steps

The prompt guides the AI through product lifecycle analysis:

**Step 1: Performance Analysis**

- Review sales velocity and trends
- Identify slow-moving products
- Calculate inventory turnover rates

**Step 2: Lifecycle Stage Classification**

- Categorize products (introduction, growth, maturity, decline)
- Identify obsolete or discontinued products
- Flag products with excess inventory

**Step 3: Action Recommendations**

- Suggest clearance pricing for slow movers
- Recommend discontinuation of obsolete items
- Identify products for promotional focus

**Step 4: Inventory Optimization**

- Recommend inventory reductions for declining products
- Suggest forecast adjustments for lifecycle stages
- Provide reorder parameter changes

#### When to Use

Use the product lifecycle review when you need to:

- Conduct regular product portfolio reviews
- Identify slow-moving inventory to clear
- Make discontinuation decisions
- Optimize inventory investment across products

## Prompt vs Tool Comparison

| Aspect           | Prompts                                 | Tools                            |
| ---------------- | --------------------------------------- | -------------------------------- |
| **Purpose**      | Multi-step workflow guidance            | Single specific action           |
| **Complexity**   | High-level business processes           | Low-level API operations         |
| **Output**       | Structured reports with recommendations | Raw data or success confirmation |
| **User Control** | AI follows guided template              | User calls directly              |
| **Best For**     | Complex tasks requiring multiple steps  | Simple direct operations         |
| **Examples**     | Purchasing review, forecast analysis    | Create product, get inventory    |

## Implementation Details

### Prompt Structure

All prompts follow this pattern:

```python
async def _prompt_name(
    param1: str,
    param2: int = default_value,
    context: Context | None = None,
) -> list[Message]:
    """Prompt implementation."""
    # Fetch dynamic context if needed
    # Construct prompt content
    # Return list of Message objects
    return [Message(content=combined_content, role="user")]
```

### Message Roles

MCP supports two message roles:

- `user`: Instructions and parameters (used for all prompts)
- `assistant`: AI responses (not used in prompt definitions)

Note: MCP does not support `system` role. System instructions are included in the user
message content.

### Dynamic Context

Prompts can fetch dynamic data when `context` is provided:

```python
if context:
    try:
        services = get_services(context)
        # Fetch location, product counts, etc.
        # Keep fast (< 100ms)
    except Exception as e:
        logger.warning(f"Failed to fetch context: {e}")
```

### Token Budget

Prompts should stay under 5KB total size to ensure:

- Fast loading and processing
- Compatibility with all MCP clients
- Reasonable context window usage

## Testing Prompts

### Unit Tests

Each prompt should have comprehensive tests:

```python
@pytest.mark.asyncio
async def test_prompt_structure():
    """Test prompt returns correct structure."""
    messages = await _prompt_name("param", 30, None)
    assert len(messages) == 1
    assert messages[0].role == "user"

@pytest.mark.asyncio
async def test_prompt_token_size():
    """Test prompt stays within budget."""
    messages = await _prompt_name("param", 30, None)
    total_size = len(messages[0].content.text)
    assert total_size < 5000
```

### Manual Testing

**With MCP Inspector:**

```bash
npx @modelcontextprotocol/inspector uv run --package stocktrim-mcp-server stocktrim-mcp-server
```

**With Claude Desktop:**

1. Configure server in `claude_desktop_config.json`
1. Restart Claude Desktop
1. Use prompt via natural language or direct invocation

## Adding New Prompts

To add a new prompt:

1. **Implement in `workflows.py`**:

   ```python
   async def _new_workflow(
       param1: str,
       context: Context | None = None,
   ) -> list[Message]:
       # Implementation
       pass
   ```

1. **Register in `register_workflow_prompts()`**:

   ```python
   @mcp.prompt()
   async def new_workflow(
       param1: str = Field(..., description="Description"),
       context: Context | None = None,
   ) -> list[Message]:
       """Docstring."""
       return await _new_workflow(param1, context)
   ```

1. **Add comprehensive tests** in `test_workflows.py`

1. **Document in this file** with all sections

1. **Run tests and linting**:

   ```bash
   uv run poe check
   ```

## Related Documentation

- [Available Tools](./tools.md) - MCP tools used by prompts
- [Resources](./overview.md#resources) - Read-only data resources
- [Workflow Examples](./examples.md) - Complete workflow walkthroughs
- [MCP Prompts Specification](https://modelcontextprotocol.io/docs/concepts/prompts) -
  Official MCP documentation
