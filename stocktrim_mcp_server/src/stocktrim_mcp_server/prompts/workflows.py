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


async def _purchasing_workflow(
    location_code: str,
    days_threshold: int,
    context: Context | None = None,
) -> list[Message]:
    """Comprehensive purchasing review and order generation.

    This prompt guides the AI through:
    1. Analyze reorder requirements
    2. Group products by supplier
    3. Generate purchase orders
    4. Provide cost analysis and recommendations

    Expected duration: 3-5 minutes

    Tools used:
    - review_urgent_order_requirements
    - generate_purchase_orders_from_urgent_items

    Resources:
    - stocktrim://reports/urgent-orders
    - stocktrim://reports/supplier-directory
    - stocktrim://products/{code}
    - stocktrim://suppliers/{code}
    """

    # Fetch dynamic data if context provided
    dynamic_context = ""
    if context:
        try:
            _ = get_services(context)  # Placeholder for future location lookup
            # Could optionally fetch location details, product count, etc.
            # Keep this fast (< 100ms)
            # For now, just note that analysis will proceed
            dynamic_context = (
                f"Note: Analysis will proceed for location '{location_code}'."
            )
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic context: {e}")
            dynamic_context = f"Note: Could not verify location '{location_code}'. Proceeding with analysis if products exist for this location."

    current_date = datetime.now().strftime("%Y-%m-%d")

    # MCP prompts only support "user" and "assistant" roles
    # Combine system instructions and user message into a single user message
    combined_msg = f"""You are an expert inventory purchasing analyst. Please conduct a comprehensive purchasing review for location {location_code}.

**Review Parameters:**
- Location: {location_code}
- Days threshold: {days_threshold} days of stock
- Review date: {current_date}

{dynamic_context}

**Your Role:**

Guide the user through:
1. Analyzing reorder requirements
2. Grouping orders by supplier
3. Generating purchase orders
4. Providing cost analysis and recommendations

**Process Steps:**

**Step 1: Analyze Requirements**
- Use review_urgent_order_requirements tool with {days_threshold}-day threshold
- Review stocktrim://reports/urgent-orders resource for context
- Identify products needing reorder
- Note any critical items (< 7 days stock)

**Step 2: Group by Supplier**
- Organize products by supplier
- Calculate total units and cost per supplier
- Check stocktrim://reports/supplier-directory for supplier details
- Identify any minimum order requirements

**Step 3: Generate Purchase Orders**
- Use generate_purchase_orders_from_urgent_items for each supplier
- Start with suppliers having critical items
- Review generated PO details
- Flag any issues (inactive suppliers, cost anomalies)

**Step 4: Summary and Recommendations**
- Total products ordered across all POs
- Total cost by supplier and overall
- Expected delivery timeline
- Items requiring special approval (high cost, new products, inactive suppliers)
- Budget considerations

**Best Practices:**

- Always prioritize critical items (< 7 days stock)
- Group orders by supplier to minimize shipments
- Verify supplier status before generating POs
- Flag cost anomalies for review
- Provide clear approval recommendations

**Tools Available:**

- review_urgent_order_requirements: Analyze what needs to be ordered
- generate_purchase_orders_from_urgent_items: Create POs for urgent items

**Resources Available:**

- stocktrim://reports/urgent-orders: Current urgent order requirements
- stocktrim://reports/supplier-directory: Supplier information
- stocktrim://products/{{code}}: Individual product details
- stocktrim://suppliers/{{code}}: Individual supplier details

**Output Format:**

Provide a structured markdown report with:
1. Executive Summary (2-3 sentences)
2. Critical Items Section (< 7 days stock)
3. Standard Items Section (7-{days_threshold} days stock)
4. Generated Purchase Orders (one section per supplier)
5. Cost Analysis (table format)
6. Recommendations (bulleted list)
7. Approval Checklist

Use tables for data, bullets for recommendations, and clear sections for easy scanning.

---

**Your Task:**

Please execute the purchasing workflow:

1. **Analyze** current reorder requirements using the {days_threshold}-day threshold
2. **Group** products by supplier for efficient ordering
3. **Generate** purchase orders for each supplier
4. **Summarize** total costs and provide approval recommendations

Start with Step 1: Analyze reorder requirements for {location_code}."""

    return [
        Message(content=combined_msg, role="user"),
    ]


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.prompt()
    async def purchasing_workflow(
        location_code: str = Field(..., description="Location code to review"),
        days_threshold: int = Field(
            default=30, description="Days of stock threshold (default: 30)"
        ),
        context: Context | None = None,
    ) -> list[Message]:
        """Comprehensive purchasing review and order generation.

        Guides AI through analyzing reorder requirements, grouping by supplier,
        generating purchase orders, and providing cost analysis.
        """
        return await _purchasing_workflow(location_code, days_threshold, context)
