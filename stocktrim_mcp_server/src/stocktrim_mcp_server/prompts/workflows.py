"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from datetime import datetime

from fastmcp import Context, FastMCP
from fastmcp.prompts.prompt import Message
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


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

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
