"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import Context, FastMCP
from fastmcp.prompts.prompt import Message
from pydantic import Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger(__name__)


async def _stockout_prevention(
    location_code: str,
    days_ahead: int,
    context: Context | None = None,
) -> list[Message]:
    """Proactive stockout prevention workflow.

    This prompt guides the AI through:
    1. Risk Analysis: Identify products at risk
    2. Gap Identification: Review current inventory levels
    3. Forecast Review: Check forecasts for at-risk products
    4. Preventive Action: Generate POs before stockouts occur

    Expected duration: 2-4 minutes

    Tools used:
    - review_urgent_order_requirements
    - generate_purchase_orders_from_urgent_items
    - forecasts_get_for_products

    Resources:
    - stocktrim://reports/inventory-status
    - stocktrim://reports/urgent-orders
    - stocktrim://products/{code}
    """

    # Fetch dynamic data if context provided
    if context:
        try:
            get_services(context)
            # Could optionally fetch location details, product count, etc.
            # Keep this fast (< 100ms)
            # For now, just include current date
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic context: {e}")

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Empty dynamic context for now - could be populated with location details, etc.
    dynamic_context = ""

    # MCP prompts use a single user message with embedded instructions
    prompt_msg = f"""# Stockout Prevention Analysis

You are an expert inventory management analyst conducting a proactive stockout prevention analysis.

## Analysis Parameters

- **Location:** {location_code}
- **Forecast horizon:** {days_ahead} days
- **Analysis date:** {current_date}

{dynamic_context}

## Your Role

Execute a comprehensive stockout prevention workflow to:
1. Analyze inventory risks and identify products at risk of stockout
2. Review current inventory levels and forecast data
3. Identify root causes (demand spikes, lead time issues, forecast gaps)
4. Generate preventive purchase orders before stockouts occur
5. Recommend safety stock or forecast adjustments

## Process Steps

### Step 1: Risk Analysis
- Use `review_urgent_order_requirements` tool with days_ahead parameter of {days_ahead}
- Review `stocktrim://reports/urgent-orders` resource for context
- Identify products at risk of stockout within the {days_ahead}-day forecast horizon
- Categorize by urgency:
  - **Critical:** < 7 days stock remaining
  - **Warning:** 7-14 days stock remaining
  - **Watch:** 14+ days stock remaining
- Note any products with declining trends

### Step 2: Gap Identification
- Review `stocktrim://reports/inventory-status` for current levels
- Compare current stock against forecast demand
- Identify gaps between stock and projected needs
- Check for products with recent stockout history
- Flag items with inadequate safety stock

### Step 3: Forecast Review
- Use `forecasts_get_for_products` for at-risk products
- Analyze demand patterns and trends
- Check for seasonality or unusual spikes
- Verify forecast accuracy based on historical data
- Identify any forecast anomalies requiring attention

### Step 4: Preventive Action
- Use `generate_purchase_orders_from_urgent_items` for each supplier
- Group orders by supplier for efficiency
- Consider lead times in order timing
- Calculate order quantities to prevent stockouts
- Flag products requiring immediate attention
- Provide clear justification for each order

### Step 5: Recommendations
- Identify products needing safety stock adjustments
- Recommend forecast parameter changes
- Suggest inventory policy improvements
- Flag systematic issues (consistent under-ordering, lead time problems)
- Provide cost analysis and budget impact

## Best Practices

- Always prioritize critical items (< 7 days stock)
- Consider supplier lead times when calculating order urgency
- Look for patterns indicating systematic issues
- Balance prevention costs against stockout risks
- Flag products with declining trends for special attention
- Recommend proactive measures, not just reactive orders
- Consider seasonal patterns in risk assessment
- Verify supplier availability before recommending orders

## Tools Available

- `review_urgent_order_requirements`: Analyze reorder needs within time horizon
- `generate_purchase_orders_from_urgent_items`: Create preventive POs
- `forecasts_get_for_products`: Review forecast data for risk assessment

## Resources Available

- `stocktrim://reports/inventory-status`: Current inventory levels
- `stocktrim://reports/urgent-orders`: Urgent reorder requirements
- `stocktrim://products/{{code}}`: Individual product details
- `stocktrim://suppliers/{{code}}`: Supplier information and lead times

## Output Format

Provide a structured markdown report with:
1. **Executive Summary** (2-3 sentences on overall risk level)
2. **Risk Categories Section:**
   - Critical Items (< 7 days) - immediate action needed
   - Warning Items (7-14 days) - preventive action recommended
   - Watch Items (14+ days) - monitoring needed
3. **Root Cause Analysis** (common patterns identified)
4. **Preventive Purchase Orders** (one section per supplier)
5. **Inventory Policy Recommendations** (bulleted list)
6. **Safety Stock Adjustments** (table format)
7. **Action Items** (prioritized checklist)

Use tables for data, bullets for recommendations, and clear sections for easy scanning.
Focus on prevention and proactive measures rather than reactive responses.

---

**Start with Step 1: Risk identification for {location_code}.**"""

    return [Message(content=prompt_msg, role="user")]


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.prompt()
    async def stockout_prevention(
        location_code: str = Field(..., description="Location code to analyze"),
        days_ahead: int = Field(
            default=14, description="Days ahead to forecast (default: 14)"
        ),
        context: Context | None = None,
    ) -> list[Message]:
        """Proactive stockout prevention workflow: analyze inventory levels, identify gaps, and create preventive purchase orders."""
        return await _stockout_prevention(location_code, days_ahead, context)
