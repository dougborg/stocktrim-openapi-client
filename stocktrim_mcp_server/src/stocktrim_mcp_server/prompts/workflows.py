"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import Context, FastMCP
from fastmcp.prompts.prompt import Message
from mcp.types import PromptMessage, TextContent
from pydantic import Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger(__name__)


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
    # Future: Could optionally fetch location details, product count, etc.
    # Keep this fast (< 100ms)
    dynamic_context = ""
    if context:
        # For now, just note that analysis will proceed
        # When implementing location lookup:
        # services = get_services(context)
        # location = await services.locations.get_by_code(location_code)
        dynamic_context = f"Note: Analysis will proceed for location '{location_code}'."

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
    # Note: Dynamic context fetching is not yet implemented but infrastructure is in place
    if context:
        try:
            _ = get_services(
                context
            )  # Validate services are available; result unused for now
            # Could optionally fetch location details, product count, etc.
            # Keep this fast (< 100ms)
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic context: {e}")

    current_date = datetime.now().strftime("%Y-%m-%d")

    # MCP prompts use a single user message with embedded instructions
    prompt_msg = f"""# Stockout Prevention Analysis

You are an expert inventory management analyst conducting a proactive stockout prevention analysis.

## Analysis Parameters

- **Location:** {location_code}
- **Forecast horizon:** {days_ahead} days
- **Analysis date:** {current_date}

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

    # Register product_lifecycle_review prompt
    mcp.prompt()(product_lifecycle_review)
