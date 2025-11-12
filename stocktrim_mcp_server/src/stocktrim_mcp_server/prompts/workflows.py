"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent
from pydantic import BaseModel, Field

from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger(__name__)


class ProductLifecycleReviewParams(BaseModel):
    """Parameters for product lifecycle review prompt."""

    category: str = Field(
        default="all", description="Product category to review (default: 'all')"
    )
    include_inactive: bool = Field(
        default=False, description="Include discontinued/inactive products"
    )


def product_lifecycle_review(
    category: str = "all", include_inactive: bool = False
) -> list[PromptMessage]:
    """Review product portfolio, identify optimization opportunities, and configure products.

    Guide AI through portfolio optimization and product configuration workflow:
    1. Portfolio Overview: List products in category
    2. Performance Analysis: Review sales, forecasts, inventory turns
    3. Configuration Review: Check forecasting settings, supplier assignments
    4. Optimization: Configure forecasts, update suppliers, flag for discontinuation

    Analysis areas:
    - Slow-moving products (low turns)
    - Overstock risks (high inventory, low demand)
    - Forecast accuracy per product
    - Supplier consolidation opportunities
    - Missing configurations (no forecast, no supplier)

    Args:
        category: Product category to review (default: 'all')
        include_inactive: Include discontinued/inactive products (default: False)

    Returns:
        List of prompt messages guiding the workflow
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    category_display = category if category != "all" else "all categories"

    # System message - guide AI through the workflow
    system_message = """You are a StockTrim inventory management expert conducting a product lifecycle review.

Your goal is to optimize the product portfolio through systematic analysis and configuration.

**Workflow Steps:**

1. **Portfolio Overview**
   - List all products in the category using `list_products`
   - Summarize total count, active vs inactive
   - Note any immediate concerns (e.g., many discontinued items)

2. **Performance Analysis**
   - For each product, review:
     * Sales history and trends
     * Current inventory levels vs demand
     * Inventory turnover rate
     * Forecast accuracy (if available)
   - Use `forecasts_get_for_products` to get forecast data
   - Access `stocktrim://reports/inventory-status` for inventory metrics

3. **Configuration Review**
   - Check each product's configuration:
     * Is forecasting enabled? (ignore_seasonality flag)
     * Are suppliers properly assigned?
     * Are lead times accurate?
   - Flag products with missing or incomplete configuration

4. **Optimization Recommendations**
   - Identify optimization opportunities:
     * **Slow movers**: Products with low turnover - consider discontinuation
     * **Overstock risks**: High inventory with declining demand - adjust forecast settings
     * **Forecast gaps**: Products without forecast configuration - enable forecasting
     * **Supplier consolidation**: Multiple suppliers for similar products - rationalize
   - Prioritize actions by business impact

5. **Execute Configuration Changes**
   - Use `configure_product` to update product settings
   - Use `update_forecast_settings` to adjust forecast parameters
   - Document all changes and rationale

**Analysis Focus Areas:**
- Slow-moving products (inventory turnover < 4x per year)
- Overstock situations (inventory > 90 days of demand)
- Forecast accuracy issues (high variance between forecast and actual)
- Supplier consolidation opportunities
- Missing configurations (no forecast settings, no supplier mappings)

**Best Practices:**
- Always review product details using `stocktrim://products/{code}` before making changes
- Consider business context (seasonal products, new launches, etc.)
- Document reasoning for configuration changes
- Prioritize high-value or high-volume products
- Be conservative with discontinuation recommendations"""

    # User message - specific request with parameters
    user_message = f"""Conduct product lifecycle review for {category_display}.

**Parameters:**
- Category: {category}
- Include inactive: {include_inactive}
- Review date: {current_date}

**Your Task:**

1. Review product portfolio in category
2. Analyze performance metrics
3. Identify optimization opportunities
4. Configure forecasts and suppliers as needed

Start with portfolio overview using the `list_products` tool."""

    return [
        PromptMessage(
            role="assistant", content=TextContent(type="text", text=system_message)
        ),
        PromptMessage(role="user", content=TextContent(type="text", text=user_message)),
    ]


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    # Register product_lifecycle_review prompt
    mcp.prompt()(product_lifecycle_review)
