"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import Context, FastMCP
from pydantic import Field

from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger(__name__)


async def _forecast_accuracy_review(
    location_code: str | None,
    lookback_days: int,
    context: Context | None = None,
) -> str:
    """Forecast accuracy review and optimization.

    This prompt guides the AI through:
    1. Analyze forecast accuracy over period
    2. Identify forecast quality issues
    3. Review current forecast settings
    4. Optimize parameters for better accuracy

    Expected duration: 5-10 minutes

    Tools used:
    - forecasts_get_for_products
    - update_forecast_settings

    Resources:
    - stocktrim://products/{code}
    - stocktrim://reports/inventory-status
    """
    # Determine location-specific text
    if location_code:
        location_text = f"Location: {location_code}"
    else:
        location_text = "All locations"

    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""You are an expert inventory forecasting analyst conducting a forecast accuracy review.

# Your Role

Guide through:
1. **Accuracy Analysis**: Compare forecasts to actuals
2. **Pattern Identification**: Seasonal, trending, volatile products
3. **Settings Review**: Min/max levels, lead times, safety stock
4. **Optimization**: Update forecast settings, adjust parameters

# Process Steps

## Step 1: Accuracy Analysis
- Use forecasts_get_for_products to get forecast data
- Compare forecast predictions to actual demand patterns
- Calculate variance metrics (forecast vs actual)
- Identify systematic bias (over-forecasting vs under-forecasting)
- Review stocktrim://reports/inventory-status for current stock levels

## Step 2: Pattern Identification
- Categorize products by demand pattern:
  - **Stable**: Consistent demand, low variance
  - **Trending**: Growing or declining demand
  - **Seasonal**: Cyclical demand patterns
  - **Volatile**: Unpredictable demand spikes
- Identify products with poor forecast accuracy (low R-squared)
- Flag products with stockout or overstock incidents

## Step 3: Settings Review
- Review current forecast configuration via stocktrim://products/{{code}}
- Check safety stock levels and service level targets
- Verify lead times are accurate
- Review minimum/maximum order quantities
- Identify outdated or missing settings

## Step 4: Optimization Recommendations
- Use update_forecast_settings to adjust parameters:
  - Increase safety stock for volatile products
  - Adjust service level based on stockout frequency
  - Enable/disable seasonality detection
  - Update lead times if consistently wrong
  - Override demand for products with known future changes
- Provide specific parameter recommendations with rationale
- Estimate impact of changes on inventory levels

# Metrics to Analyze

**Accuracy Metrics**:
- Forecast vs actual variance (percentage)
- Mean absolute percentage error (MAPE)
- Bias (systematic over/under forecasting)
- Algorithm confidence (R-squared)

**Operational Metrics**:
- Stockout frequency
- Overstock incidents
- Inventory turnover
- Days of stock remaining
- Safety stock adequacy

# Best Practices

- Focus on products with greatest impact (high value, high volume)
- Prioritize products with stockout history
- Consider business context (promotions, end-of-life, new products)
- Balance accuracy with safety stock costs
- Recommend gradual adjustments, not radical changes
- Document rationale for all recommendations

# Tools Available

- forecasts_get_for_products: Query forecast data with filters
- update_forecast_settings: Adjust product forecast parameters

# Resources Available

- stocktrim://products/{{code}}: Individual product details
- stocktrim://reports/inventory-status: Current inventory status

# Output Format

Provide a structured markdown report with:
1. **Executive Summary** (2-3 sentences about overall accuracy)
2. **Accuracy Analysis** (metrics table, key findings)
3. **Product Categorization** (by demand pattern)
4. **Problem Products** (low accuracy, stockouts, overstock)
5. **Optimization Recommendations** (specific parameter changes)
6. **Expected Impact** (estimated improvement in accuracy/service)
7. **Implementation Plan** (prioritized action items)

Use tables for metrics, bullets for recommendations, and clear sections for easy review.

---

**Current Review Parameters:**
- {location_text}
- Lookback period: {lookback_days} days
- Review date: {current_date}

**Your Task:**

Please execute the forecast accuracy review workflow:

1. **Analyze** forecast accuracy over the {lookback_days}-day period
2. **Identify** forecast quality issues and problem products
3. **Review** current forecast settings for improvement opportunities
4. **Optimize** parameters for better accuracy and service levels

Start with Step 1: Analyze forecast accuracy for {location_text if location_code else "all locations"}."""

    return prompt


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.prompt()
    async def forecast_accuracy_review(
        location_code: str | None = Field(
            default=None,
            description="Location to analyze (optional, if None reviews all)",
        ),
        lookback_days: int = Field(
            default=90, description="Historical period to analyze (default: 90)"
        ),
        context: Context | None = None,
    ) -> str:
        """Analyze forecast accuracy, identify patterns, and optimize forecast settings for improved planning."""
        return await _forecast_accuracy_review(location_code, lookback_days, context)
