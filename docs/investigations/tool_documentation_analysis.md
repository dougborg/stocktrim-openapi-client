# Tool Documentation Analysis: StockTrim MCP Server

## Executive Summary

The StockTrim MCP server uses a **manual documentation pattern** where tool descriptions
are defined in docstrings. FastMCP extracts these descriptions automatically using
`inspect.getdoc()`, but parameter documentation is manually defined through Pydantic
`Field()` descriptions. There are currently no auto-generation utilities, but FastMCP
provides the infrastructure to build one.

______________________________________________________________________

## 1. CURRENT DOCUMENTATION PATTERN

### 1.1 Tool Registration Approach

**Location**: `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/`

**Pattern**: Non-decorator based registration

```python
# Tools are regular async functions without @mcp.tool decorators
async def get_customer(
    request: GetCustomerRequest, context: Context
) -> CustomerInfo | None:
    """Get a customer by code.

    This tool retrieves detailed information about a specific customer
    from StockTrim.

    Args:
        request: Request containing customer code
        context: Server context with StockTrimClient

    Returns:
        CustomerInfo if found, None if not found

    Example:
        Request: {"code": "CUST-001"}
        Returns: {"code": "CUST-001", "name": "Customer Name", ...}
    """
    # implementation...

# Registration happens in register_tools() function
def register_tools(mcp: FastMCP) -> None:
    """Register customer tools with FastMCP server."""
    mcp.tool()(get_customer)
    mcp.tool()(list_customers)
```

**Key Files**:

- `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/__init__.py`
- `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/__init__.py`
- `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/workflows/__init__.py`

### 1.2 Tool Description Sources

#### A. Function Docstrings (Primary)

- **Location**: First docstring in async function
- **Extracted by**: FastMCP's `ParsedFunction.from_function()` at line 403 via
  `inspect.getdoc(fn)`
- **Content**: High-level tool description, often 2-3 sentences
- **Format**: Google-style docstrings with Args, Returns, Example sections

**Example from products.py**:

```python
async def get_product(
    request: GetProductRequest, context: Context
) -> ProductInfo | None:
    """Get a product by code.

    This tool retrieves detailed information about a specific product
    from StockTrim inventory.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        ProductInfo if found, None if not found

    Example:
        Request: {"code": "WIDGET-001"}
        Returns: {"code": "WIDGET-001", "description": "Widget", ...}
    """
```

#### B. Pydantic Field Descriptions (Parameter Level)

- **Location**: `Field(..., description="...")` in Request models
- **Extracted by**: Pydantic's schema generation (handled by FastMCP)
- **Content**: Parameter-specific documentation
- **Format**: Short, single-line descriptions

**Example from purchase_orders.py**:

```python
class CreatePurchaseOrderRequest(BaseModel):
    """Request model for creating a purchase order."""

    supplier_code: str = Field(..., description="Supplier code")
    supplier_name: str | None = Field(default=None, description="Supplier name")
    line_items: list[LineItemRequest] = Field(
        ..., description="Line items for the purchase order", min_length=1
    )
    order_date: datetime | None = Field(
        default=None,
        description="Order date (ISO format). Defaults to current date if not provided.",
    )
```

#### C. Response Model Descriptions

- **Location**: `Field()` descriptions in response models
- **Used for**: Output documentation
- **Format**: Pydantic field descriptions

**Example from urgent_orders.py**:

```python
class UrgentItemInfo(BaseModel):
    """Information about an urgent item needing reorder."""

    product_code: str | None = Field(description="Product code")
    current_stock: float | None = Field(description="Current stock on hand")
    days_until_stock_out: int | None = Field(description="Days until stock out")
```

### 1.3 Extended Documentation Pattern (Workflow Tools)

**Location**: Workflow tools in `tools/workflows/`

**Extended Pattern**: Markdown-formatted docstrings with sections for:

- `## How It Works`: Multi-step explanation
- `## Common Use Cases`: Enumerated scenarios with parameters
- `## Typical Workflow`: Step-by-step workflow description
- `## See Also`: Cross-references to related tools

**Example from urgent_orders.py (review_urgent_order_requirements)**:

```python
async def review_urgent_order_requirements(
    request: ReviewUrgentOrdersRequest, ctx: Context
) -> ReviewUrgentOrdersResponse:
    """Review items that need urgent reordering based on forecast data.

    This workflow tool analyzes StockTrim's forecast and order plan data to identify
    items approaching stockout. Results are grouped by supplier to facilitate
    efficient purchase order generation.

    ## How It Works

    1. Queries the order plan for items with days_until_stock_out < threshold
    2. Enriches data with supplier information from product catalog
    3. Groups items by supplier for consolidated purchasing
    4. Calculates estimated costs per supplier and overall

    ## Common Use Cases

    - **Weekly/Monthly Reorder Cycles**: Run with `days_threshold=30` to identify
      items needing reorder in the next month
    - **Urgent Restocking**: Use lower threshold (7-14 days) for critical items
    - **Supplier-Specific Review**: Filter by `supplier_codes` to review specific vendors
    - **Multi-Location Management**: Use `location_codes` to check each warehouse

    ## Typical Workflow

    1. Run `forecasts_update_and_monitor` to ensure forecasts are current
    2. Call this tool to identify urgent items grouped by supplier
    3. Review the recommendations (items, quantities, costs)
    4. Call `generate_purchase_orders_from_urgent_items` for approved suppliers
    5. Review draft POs in StockTrim UI before approving

    Args:
        request: Request with filters for urgent items
        context: Server context with StockTrimClient

    Returns:
        ReviewUrgentOrdersResponse with items grouped by supplier, including:
        - List of suppliers with urgent items
        - Items per supplier with stock levels and recommendations
        - Total estimated costs per supplier and overall

    Example:
        Request: {
            "days_threshold": 30,
            "location_codes": ["WAREHOUSE-A"],
            "supplier_codes": ["SUP-001"]
        }
        Returns: {
            "suppliers": [
                {
                    "supplier_code": "SUP-001",
                    "items": [...],
                    "total_items": 1,
                    "total_estimated_cost": 3100.00
                }
            ],
            "total_items": 1,
            "total_estimated_cost": 3100.00
        }

    See Also:
        - Complete workflow: docs/mcp-server/examples.md#workflow-1-automated-inventory-reordering
        - `generate_purchase_orders_from_urgent_items`: Auto-generate POs from this data
        - `forecasts_update_and_monitor`: Ensure forecasts are current before using this tool
    """
```

### 1.4 High-Risk Operation Markers

**Pattern**: Emoji markers in docstrings for destructive operations

```python
async def delete_product(
    request: DeleteProductRequest, context: Context
) -> DeleteProductResponse:
    """Delete a product by code.

    🔴 HIGH-RISK OPERATION: This action permanently deletes product data
    and cannot be undone. User confirmation is required via elicitation.

    This tool deletes a product from StockTrim inventory after obtaining
    explicit user confirmation through the MCP elicitation protocol.
    ...
    """
```

______________________________________________________________________

## 2. TOOL SIGNATURE ANALYSIS

### 2.1 Consistent Pattern

All tools follow this signature:

```python
async def <tool_name>(
    request: <RequestModel>,
    context: Context
) -> <ResponseType>
```

**Components**:

- **Function Name**: Snake_case, descriptive (e.g., `get_customer`, `list_products`,
  `review_urgent_order_requirements`)
- **Request Parameter**: Pydantic BaseModel with `Field()` descriptions for each
  parameter
- **Context Parameter**: FastMCP `Context` object (automatically injected by FastMCP)
- **Return Type**: Response model (BaseModel or None for get operations)

### 2.2 Request/Response Model Pattern

**Foundation Tools** (CRUD operations):

```python
class GetProductRequest(BaseModel):
    """Request model for getting a product."""
    code: str = Field(..., description="Product code to retrieve")

class ProductInfo(BaseModel):
    """Product information."""
    code: str
    description: str | None
    unit_of_measurement: str | None
    is_active: bool
    cost_price: float | None
    selling_price: float | None

async def get_product(
    request: GetProductRequest, context: Context
) -> ProductInfo | None:
```

**Workflow Tools** (Complex operations):

```python
class ReviewUrgentOrdersRequest(BaseModel):
    """Request for reviewing urgent order requirements."""
    days_threshold: int = Field(
        default=30, description="Days until stockout threshold (default: 30)"
    )
    location_codes: list[str] | None = Field(
        default=None, description="Filter by specific locations"
    )

class UrgentItemInfo(BaseModel):
    """Information about an urgent item needing reorder."""
    product_code: str | None = Field(description="Product code")
    # ... more fields

async def review_urgent_order_requirements(
    request: ReviewUrgentOrdersRequest, ctx: Context
) -> ReviewUrgentOrdersResponse:
```

### 2.3 Type Hints and Validation

All tools use:

- **Type hints**: Full type annotations with union types (`str | None`)
- **Pydantic validation**: Required fields (`...`), optional fields (`default=None`)
- **Range validation**: `min_length=1`, `gt=0` for quantities
- **Field constraints**: Through Pydantic `Field()`

______________________________________________________________________

## 3. FASTMCP INTEGRATION & AUTO-GENERATION SUPPORT

### 3.1 How FastMCP Processes Tool Descriptions

**File**: `.venv/lib/python3.13/site-packages/fastmcp/tools/tool.py`

**Process**:

1. `FunctionTool.from_function()` (line 248) receives a function
1. Calls `ParsedFunction.from_function()` (line 265) to extract metadata
1. `ParsedFunction.from_function()` uses `inspect.getdoc(fn)` (line 403) to extract
   docstring
1. Docstring becomes `description` field in ParsedFunction
1. If no explicit description passed, `parsed_fn.description` is used (line 297)

**Key Code**:

```python
@classmethod
def from_function(
    cls,
    fn: Callable[..., Any],
    exclude_args: list[str] | None = None,
    # ...
) -> ParsedFunction:
    # Line 402-403: Extract function name and docstring
    fn_name = getattr(fn, "__name__", None) or fn.__class__.__name__
    fn_doc = inspect.getdoc(fn)

    # Lines 419-423: Extract input schema (parameters)
    input_type_adapter = get_cached_typeadapter(fn)
    input_schema = input_type_adapter.json_schema()
    input_schema = compress_schema(
        input_schema, prune_params=prune_params, prune_titles=True
    )

    # Returns ParsedFunction with description
    return cls(
        fn=fn,
        name=fn_name,
        description=fn_doc,  # Line 492: Uses docstring as description
        input_schema=input_schema,
        output_schema=output_schema or None,
    )
```

### 3.2 What FastMCP Extracts Automatically

- **Tool Name**: From function `__name__`
- **Tool Description**: From function docstring via `inspect.getdoc()`
- **Parameter Names & Types**: From function signature and type hints
- **Parameter Descriptions**: From Pydantic `Field(description=...)`
- **Output Schema**: From return type annotation (via Pydantic schema generation)

### 3.3 What FastMCP Does NOT Auto-Generate

- **High-level workflow documentation**: Sections like "## How It Works", "## Common Use
  Cases"
- **Risk level markers**: 🔴 HIGH-RISK, etc.
- **Cross-references**: "See Also" sections
- **Example JSON**: In complex workflows
- **Semantic grouping**: How tools relate to each other

______________________________________________________________________

## 4. AUTO-GENERATION POSSIBILITIES

### 4.1 Low-Hanging Fruit (Easy to Implement)

#### A. Parameter Documentation from Docstring

**Current**: Manual `Field(description=...)` in request models **Possible**: Extract
parameter descriptions from function docstring Args section

```python
# Current (manual):
class CreateProductRequest(BaseModel):
    code: str = Field(..., description="Unique product code")
    description: str = Field(..., description="Product description")

# Could be auto-generated from docstring Args section
async def create_product(
    request: CreateProductRequest, context: Context
) -> ProductInfo:
    """Create a new product.

    Args:
        request: Request containing product details with:
            - code: Unique product code
            - description: Product description
            - cost_price: Cost price (optional)
        context: Server context with StockTrimClient

    Returns:
        ProductInfo for the created product
    """
```

**Tool**: Write a docstring parser to extract Args and populate Field descriptions

#### B. Return Documentation from Docstring

**Current**: Manual `Field()` descriptions in response models **Possible**: Extract
descriptions from Returns section of docstring

#### C. Example Extraction

**Current**: Manual JSON examples in docstring Examples section **Possible**: Parse and
validate Examples section, generate documentation

### 4.2 Medium Effort (Requires Infrastructure)

#### A. Tool Category/Group Detection

**Possible**: Analyze tool names and docstrings to auto-group into categories

```python
# Pattern matching:
- Tools starting with "get_" or "list_" → Read operations
- Tools with "create_", "update_", "delete_" → Write operations
- Tools with "review_", "generate_", "update_and_" → Workflows
```

#### B. Risk Level Classification

**Possible**: Detect destructive keywords and auto-assign risk levels

```python
# Keywords indicating HIGH-RISK:
- "delete", "remove", "destroy", "permanently"
# Keywords indicating MEDIUM:
- "update", "modify", "change"
# Keywords indicating LOW:
- "get", "list", "retrieve", "query"
```

#### C. Markdown Documentation Generation

**Possible**: Generate markdown documentation from tool metadata

```python
# Generate:
- Parameter reference tables
- Example request/response JSON
- Tool categorization
- Risk level badges
```

### 4.3 Advanced (Requires Major Changes)

#### A. Docstring Template Validation

**Possible**: Define and enforce docstring template standards

```python
# Template:
"""<One-line summary>.

<Detailed description>.

<Optional: ## How It Works section for workflows>
<Optional: ## Common Use Cases section for workflows>

Args:
    request: <Request model description>
    context: Server context

Returns:
    <Return type description>

Example:
    <JSON example>

See Also:
    <Related tools>
"""
```

#### B. Pydantic-to-Docstring Generation

**Possible**: Use `get_type_hints()` and Pydantic field metadata to generate docstrings

```python
# Using:
from typing import get_type_hints
from pydantic import Field

# Could generate:
request_docs = generate_docstring_from_request(GetProductRequest)
# Result: structured documentation of all fields
```

______________________________________________________________________

## 5. EXISTING UTILITIES & TOOLS

### 5.1 No Current Auto-Generation Code

**Finding**: No existing code in the codebase generates documentation from signatures

### 5.2 FastMCP Built-in Support

**Location**: `.venv/lib/python3.13/site-packages/fastmcp/tools/`

**Key Classes/Functions**:

- `ParsedFunction.from_function()` - Extracts metadata from functions
- `FunctionTool.from_function()` - Creates Tool from function
- `Tool.from_tool()` - Creates transformed tools
- `get_cached_typeadapter()` - Gets Pydantic type adapter for validation
- `compress_schema()` - Compresses JSON schemas
- `inspect.getdoc()` - Extracts docstrings (Python stdlib)
- `get_type_hints()` - Resolves type hints (Python stdlib)

### 5.3 Template Files

**Location**:
`stocktrim_mcp_server/src/stocktrim_mcp_server/templates/`

**Current Templates** (for status messages, not tool documentation):

- `forecast_complete.md` - Status message template with placeholders like
  `{elapsed:.1f}`
- `forecast_failed.md` - Failure message template
- `forecast_triggered.md` - Initial status message template
- `forecast_query_empty.md` - Empty results message
- `forecast_query_failed.md` - Query error message
- `forecast_timeout.md` - Timeout message

**No templates for tool documentation** - All tool descriptions are inline docstrings

______________________________________________________________________

## 6. DOCUMENTATION EXAMPLES

### 6.1 Foundation Tool Example

**File**:
`stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/customers.py`

```python
class GetCustomerRequest(BaseModel):
    """Request model for getting a customer."""
    code: str = Field(..., description="Customer code to retrieve")

class CustomerInfo(BaseModel):
    """Customer information."""
    code: str
    name: str | None
    email: str | None
    phone: str | None
    address: str | None

async def get_customer(
    request: GetCustomerRequest, context: Context
) -> CustomerInfo | None:
    """Get a customer by code.

    This tool retrieves detailed information about a specific customer
    from StockTrim.

    Args:
        request: Request containing customer code
        context: Server context with StockTrimClient

    Returns:
        CustomerInfo if found, None if not found

    Example:
        Request: {"code": "CUST-001"}
        Returns: {"code": "CUST-001", "name": "Customer Name", ...}
    """
    services = get_services(context)
    customer = await services.customers.get_by_code(request.code)

    if not customer:
        return None

    return CustomerInfo(
        code=customer.code or "",
        name=customer.name,
        email=customer.email_address,
        phone=customer.phone,
        address=customer.street_address,
    )
```

### 6.2 Workflow Tool Example

**File**:
`stocktrim_mcp_server/src/stocktrim_mcp_server/tools/workflows/urgent_orders.py`

```python
class ReviewUrgentOrdersRequest(BaseModel):
    """Request for reviewing urgent order requirements."""
    days_threshold: int = Field(
        default=30, description="Days until stockout threshold (default: 30)"
    )
    location_codes: list[str] | None = Field(
        default=None, description="Filter by specific locations"
    )
    category: str | None = Field(default=None, description="Filter by product category")
    supplier_codes: list[str] | None = Field(
        default=None, description="Filter by specific suppliers"
    )

# ... response models ...

async def review_urgent_order_requirements(
    request: ReviewUrgentOrdersRequest, ctx: Context
) -> ReviewUrgentOrdersResponse:
    """Review items that need urgent reordering based on forecast data.

    This workflow tool analyzes StockTrim's forecast and order plan data to identify
    items approaching stockout. Results are grouped by supplier to facilitate
    efficient purchase order generation.

    ## How It Works

    1. Queries the order plan for items with days_until_stock_out < threshold
    2. Enriches data with supplier information from product catalog
    3. Groups items by supplier for consolidated purchasing
    4. Calculates estimated costs per supplier and overall

    ## Common Use Cases

    - **Weekly/Monthly Reorder Cycles**: Run with `days_threshold=30` to identify
      items needing reorder in the next month
    - **Urgent Restocking**: Use lower threshold (7-14 days) for critical items
    - **Supplier-Specific Review**: Filter by `supplier_codes` to review specific vendors
    - **Multi-Location Management**: Use `location_codes` to check each warehouse

    ## Typical Workflow

    1. Run `forecasts_update_and_monitor` to ensure forecasts are current
    2. Call this tool to identify urgent items grouped by supplier
    3. Review the recommendations (items, quantities, costs)
    4. Call `generate_purchase_orders_from_urgent_items` for approved suppliers
    5. Review draft POs in StockTrim UI before approving

    Args:
        request: Request with filters for urgent items
        context: Server context with StockTrimClient

    Returns:
        ReviewUrgentOrdersResponse with items grouped by supplier, including:
        - List of suppliers with urgent items
        - Items per supplier with stock levels and recommendations
        - Total estimated costs per supplier and overall

    Example:
        Request: {
            "days_threshold": 30,
            "location_codes": ["WAREHOUSE-A"],
            "supplier_codes": ["SUP-001"]
        }
        Returns: {
            "suppliers": [
                {
                    "supplier_code": "SUP-001",
                    "items": [
                        {
                            "product_code": "WIDGET-001",
                            "current_stock": 45.0,
                            "days_until_stock_out": 12,
                            "recommended_order_qty": 200.0,
                            "estimated_unit_cost": 15.50
                        }
                    ],
                    "total_items": 1,
                    "total_estimated_cost": 3100.00
                }
            ],
            "total_items": 1,
            "total_estimated_cost": 3100.00
        }

    See Also:
        - Complete workflow: docs/mcp-server/examples.md#workflow-1-automated-inventory-reordering
        - `generate_purchase_orders_from_urgent_items`: Auto-generate POs from this data
        - `forecasts_update_and_monitor`: Ensure forecasts are current before using this tool
    """
```

______________________________________________________________________

## 7. RECOMMENDATIONS

### For Immediate Implementation (Low Effort, High Value)

1. **Create docstring parser utility** in
   `stocktrim_mcp_server/src/stocktrim_mcp_server/utils/`:

   - Extract Args section descriptions
   - Extract Returns section descriptions
   - Extract Example JSON
   - Validate docstring format

1. **Create Pydantic helper** to auto-populate Field descriptions:

   - Parse function docstring
   - Extract parameter documentation
   - Populate Field(description=...) automatically

1. **Create tool metadata extractor**:

   - Iterate all registered tools
   - Extract name, description, parameters, returns
   - Generate structured JSON metadata file
   - Use for documentation generation

### For Medium-Term Implementation

1. **Docstring template enforcer**:

   - Define standard template
   - Validate all tool docstrings match template
   - Warn on missing sections

1. **Markdown documentation generator**:

   - Use extracted metadata to generate tools.md
   - Auto-update tool reference documentation
   - Include examples, parameters, risk levels

1. **Tool categorization system**:

   - Auto-detect tool category from name/docstring
   - Generate category-based tool listings

### For Long-Term Implementation

1. **Docstring auto-generation**:

   - Use LLM to generate docstrings from function signatures
   - Generate examples from request/response models
   - Generate related tools from cross-references

1. **Test documentation synchronization**:

   - Auto-generate test cases from tool documentation
   - Validate examples work with actual tools

______________________________________________________________________

## APPENDIX: File Locations Summary

### Tool Registration

- Primary:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/__init__.py`
- Foundation:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/__init__.py`
- Workflows:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/workflows/__init__.py`

### Tool Implementations

- Customers:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/customers.py`
- Products:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/products.py`
- Suppliers:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/suppliers.py`
- Locations:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/locations.py`
- Inventory:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/inventory.py`
- Purchase Orders:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/foundation/purchase_orders.py`
- Urgent Orders:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/workflows/urgent_orders.py`

### Documentation

- Tools Reference:
  `docs/mcp-server/tools.md`
- Templates:
  `stocktrim_mcp_server/src/stocktrim_mcp_server/templates/`

### FastMCP Source

- Tool Implementation: `.venv/lib/python3.13/site-packages/fastmcp/tools/tool.py`
  (ParsedFunction at line 360)
- Tool Transform: `.venv/lib/python3.13/site-packages/fastmcp/tools/tool_transform.py`
