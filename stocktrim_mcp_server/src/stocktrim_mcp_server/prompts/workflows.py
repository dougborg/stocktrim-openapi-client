"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import Context, FastMCP
from fastmcp.prompts.prompt import Message
from mcp.types import PromptMessage, TextContent
from pydantic import Field


async def _supplier_performance_review(
    supplier_code: str | None,
    period_days: int,
    context: Context | None = None,
) -> list[Message]:
    """Comprehensive supplier performance review and analysis.

    This prompt guides the AI through:
    1. Supplier overview and details
    2. Performance analysis (PO history, delivery times, costs)
    3. Trend analysis (improving/declining performance)
    4. Recommendations (consolidation, risk mitigation, contracts)

    Expected duration: 3-5 minutes

    Tools used:
    - list_purchase_orders
    - get_supplier

    Resources:
    - stocktrim://reports/supplier-directory
    - stocktrim://suppliers/{code}
    """
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Determine supplier scope
    supplier_specific_or_all = (
        f"Specific supplier: {supplier_code}" if supplier_code else "All suppliers"
    )

    prompt_content = f"""You are an expert supply chain analyst conducting a comprehensive supplier performance review.

# Analysis Parameters

- {supplier_specific_or_all}
- Analysis period: {period_days} days
- Review date: {current_date}

# Your Task

Conduct a thorough supplier performance review by:

1. Analyzing supplier performance metrics
2. Identifying optimization opportunities
3. Providing actionable recommendations
4. Highlighting risk mitigation strategies

# Process Steps

## Step 1: Supplier Overview
- Use stocktrim://reports/supplier-directory resource to get supplier list
- If specific supplier, use stocktrim://suppliers/{{code}} for details
- Review supplier basic information (contact, terms, lead times)
- Identify active vs inactive suppliers

## Step 2: Performance Analysis
- Use list_purchase_orders tool filtered by supplier and time period
- Calculate key performance indicators:
  - On-time delivery rate
  - Order accuracy
  - Average lead time vs promised lead time
  - Cost trends over time
  - Order frequency and consistency

## Step 3: Trend Analysis
- Identify improving performance patterns
- Identify declining performance patterns
- Compare suppliers against each other (if reviewing all)
- Flag any concerning trends (cost increases, delays)
- Note seasonal patterns if evident

## Step 4: Recommendations
- **Consolidation Opportunities**: Identify suppliers that could be consolidated
- **Risk Mitigation**: Flag suppliers with declining performance or single-source risks
- **Contract Renegotiation**: Suggest where better terms could be negotiated
- **Supplier Development**: Identify suppliers worth investing in
- **Alternative Sources**: Recommend backup suppliers for critical items

# Metrics to Analyze

## Delivery Performance
- On-time delivery rate (% of orders delivered on or before promised date)
- Average delay in days for late orders
- Lead time consistency (standard deviation)

## Cost Performance
- Price trends over analysis period
- Cost per unit trends
- Total spend by supplier
- Cost competitiveness compared to alternatives

## Order Accuracy
- Correct quantities received
- Correct products received
- Quality issues or returns

## Relationship Quality
- Communication responsiveness
- Problem resolution effectiveness
- Flexibility with urgent orders
- Payment terms favorability

# Best Practices

- Always analyze data for the full period specified
- Compare current performance to historical baselines
- Provide quantitative metrics whenever possible
- Be objective in assessments
- Prioritize recommendations by impact and feasibility
- Consider both cost and risk in recommendations

# Tools Available

- **list_purchase_orders**: Get PO history filtered by supplier and date range
- **get_supplier**: Get detailed supplier information

# Resources Available

- **stocktrim://reports/supplier-directory**: Complete supplier directory
- **stocktrim://suppliers/{{code}}**: Individual supplier details

# Output Format

Provide a structured markdown report with:

1. **Executive Summary** (2-3 sentences)
2. **Supplier Overview Section**
   - Number of suppliers reviewed
   - Total spend in period
   - Key statistics
3. **Performance Analysis Section**
   - Top performers (with metrics)
   - Bottom performers (with metrics)
   - Detailed metrics by supplier
4. **Trend Analysis Section**
   - Improving suppliers
   - Declining suppliers
   - Emerging patterns
5. **Recommendations Section** (prioritized bulleted list)
   - Consolidation opportunities
   - Risk mitigation actions
   - Contract renegotiation targets
   - Supplier development investments
6. **Action Items** (specific next steps)

Use tables for metrics, bullets for recommendations, and clear sections for easy scanning.

Start with the supplier overview step."""

    return [Message(content=prompt_content, role="user")]


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
    
    @mcp.prompt()  
    async def supplier_performance_review(
        supplier_code: str | None = Field(
            default=None,
            description="Specific supplier to review (optional, if None reviews all)",
        ),
        period_days: int = Field(
            default=90, description="Historical period to analyze (default: 90 days)"
        ),
        context: Context | None = None,
    ) -> list[Message]:
        """Comprehensive supplier performance review and analysis."""
        return await _supplier_performance_review(supplier_code, period_days, context)
