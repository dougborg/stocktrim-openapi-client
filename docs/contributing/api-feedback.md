# StockTrim API Feedback and Questions

This document contains constructive feedback and questions about the StockTrim Public
API, discovered while building a Python client. We hope this feedback helps improve the
API for all users!

**Version**: Based on swagger v1 (https://api.stocktrim.com/swagger/v1/swagger.yaml)
**Date**: 2025-10-28

______________________________________________________________________

## Table of Contents

- [OpenAPI Specification](#openapi-specification)
- [Response Type Consistency](#response-type-consistency)
- [Authentication Design](#authentication-design)
- [Documentation Completeness](#documentation-completeness)
- [Endpoint Conventions](#endpoint-conventions)
- [Questions for Clarification](#questions-for-clarification)

______________________________________________________________________

## OpenAPI Specification

### Missing Security Schemes

**Current State**: Authentication is defined as required header parameters
(`api-auth-id` and `api-auth-signature`) on every single endpoint (39 endpoints, 78
total parameters).

**Suggestion**: Consider using OpenAPI's `securitySchemes` and global `security`
definitions. This would:

- Reduce specification size and redundancy
- Allow API clients to handle authentication more elegantly
- Follow OpenAPI best practices for authentication
- Make it easier to update authentication requirements across all endpoints

**Example**:

```yaml
components:
  securitySchemes:
    StockTrimAuth:
      type: apiKey
      in: header
      name: api-auth-id
      description: StockTrim authentication

security:
  - StockTrimAuth: []
```

**Impact**: This would eliminate 78 parameter definitions while maintaining the same
functionality.

______________________________________________________________________

## Response Type Consistency

### GET Endpoints Returning Single Objects Instead of Arrays

Several GET endpoints return a single object when a filter parameter is provided, but
return an array when no filter is provided. This creates inconsistent return types that
are harder for clients to handle.

**Affected Endpoints**:

| Endpoint                  | Filter Parameter     | Returns w/ Filter          | Returns w/o Filter                            |
| ------------------------- | -------------------- | -------------------------- | --------------------------------------------- |
| `GET /api/Suppliers`      | `?code=X`            | `SupplierResponseDto`      | `SupplierResponseDto` (spec says single)      |
| `GET /api/PurchaseOrders` | `?referenceNumber=X` | `PurchaseOrderResponseDto` | `PurchaseOrderResponseDto` (spec says single) |
| `GET /api/Locations`      | `?code=X`            | `LocationResponseDto`      | `LocationResponseDto` (spec says single)      |

**Suggestion**: Consider always returning arrays from GET endpoints, even when filtering
to a single item:

- Single item: `[{...}]`
- Multiple items: `[{...}, {...}]`
- No items: `[]`

**Benefits**:

- Consistent return types make client code simpler
- Easier to handle edge cases (no items found)
- Follows REST best practices
- Eliminates need for type checking in client code

**Alternative**: If single-object returns are intentional for filtered queries, consider
separate endpoints:

- `GET /api/Suppliers` → returns array
- `GET /api/Suppliers/{code}` → returns single object (404 if not found)

______________________________________________________________________

### Inventory Endpoint Response Type

**Endpoint**: `POST /api/Inventory`

**Current Behavior**: Returns `PurchaseOrderResponseDto`

**Question**: Is this the intended response type? It seems unexpected that setting
inventory would return purchase order data.

**Suggestion**: Consider returning:

- An inventory-specific response DTO (e.g., `SetInventoryResponseDto`)
- The same `SetInventoryRequest` with updated values
- A simple success response

______________________________________________________________________

## Authentication Design

### Dual Authentication Headers

**Current State**: Two headers required: `api-auth-id` and `api-auth-signature`

**Questions**:

1. What is the signature algorithm? (HMAC-SHA256, etc.)
1. What data is being signed?
1. Is there documentation for generating the signature?
1. Should signatures be calculated per-request or are they static?

**Suggestion**: Consider documenting the authentication flow in the OpenAPI description
or providing a link to authentication documentation.

______________________________________________________________________

## Documentation Completeness

### Missing Operation Summaries

**Current State**: All 39 endpoints are missing the `summary` field in the OpenAPI spec.

**Example** (current):

```yaml
/api/Products:
  get:
    tags:
      - Products
    parameters:
      # ...
```

**Suggestion** (improved):

```yaml
/api/Products:
  get:
    summary: Get all products
    description: Retrieves a list of products with optional filtering by code or page number
    tags:
      - Products
    parameters:
      # ...
```

**Benefits**:

- Better documentation in auto-generated API documentation
- Improves developer experience with IDE auto-completion
- Makes the API easier to understand at a glance

______________________________________________________________________

### Missing Operation IDs

**Current State**: All 39 endpoints are missing `operationId` fields.

**Suggestion**: Add unique operation IDs to help code generators create better method
names:

```yaml
/api/Products:
  get:
    operationId: getProducts
    # ...
  post:
    operationId: createProduct
    # ...
  delete:
    operationId: deleteProduct
    # ...
```

**Benefits**:

- Generated client code has better method names
- Easier to reference specific operations in documentation
- Improves SDK quality across all languages

______________________________________________________________________

### Missing Server Configuration

**Current State**: The `servers` field is not defined in the OpenAPI spec.

**Suggestion**: Add server information to help developers:

```yaml
servers:
  - url: https://api.stocktrim.com
    description: Production API server
```

**Benefits**:

- Clients can auto-configure the base URL
- Makes it clear what the production endpoint is
- Allows for multiple environments (staging, production, etc.)

______________________________________________________________________

## Endpoint Conventions

### Inconsistent Batch Operations

**Current State**: Different endpoints have different batch operation patterns:

| Endpoint                   | POST Input    | POST Output   | Pattern         |
| -------------------------- | ------------- | ------------- | --------------- |
| `POST /api/Products`       | Single object | Single object | One-at-a-time   |
| `POST /api/Suppliers`      | Array         | Array         | Batch operation |
| `POST /api/SalesOrders`    | Single object | Single object | One-at-a-time   |
| `POST /api/PurchaseOrders` | Single object | Single object | One-at-a-time   |

**Question**: What is the intended pattern for bulk operations?

**Suggestions**:

1. **Option A - Dedicated Bulk Endpoints**: Provide separate bulk endpoints for all
   entities

   - `POST /api/Products` → single
   - `POST /api/ProductsBulk` → array (like `SalesOrdersBulk`)

1. **Option B - Unified Array Pattern**: All POST endpoints accept arrays

   - Single item: `POST /api/Products` with `[{...}]`
   - Multiple items: `POST /api/Products` with `[{...}, {...}]`

**Benefits**:

- Consistent patterns are easier to learn and use
- Reduces the need for multiple round-trips
- Improves API performance for bulk operations

______________________________________________________________________

### Delete Operation Clarity

**Question**: For DELETE endpoints that accept optional filter parameters (e.g.,
`productId`, `referenceNumber`), what happens when the parameter is omitted?

**Examples**:

- `DELETE /api/Products?productId=123` → Deletes product 123
- `DELETE /api/Products` → Deletes... all products? Returns error?

**Suggestion**: Consider:

1. Making filter parameters required for DELETE operations
1. Providing separate "delete all" endpoints if that's intended functionality
1. Documenting the behavior clearly in operation descriptions

**Safety**: This is particularly important to prevent accidental data loss.

______________________________________________________________________

## Questions for Clarification

### 1. Customer Update Response

**Endpoint**: `PUT /api/Customers`

**Input**: Single `CustomerDto` **Output**: Array of `PurchaseOrderResponseDto`

**Questions**:

- Why does updating a customer return purchase orders?
- Is this a documentation error in the OpenAPI spec?
- Should it return `CustomerDto` or `Customer`?

______________________________________________________________________

### 2. Pagination Strategy

**Endpoint**: `GET /api/Products`

**Current**: Uses `pageNo` parameter (string type)

**Questions**:

- Is there a `pageSize` or `limit` parameter available?
- How do we know when we've reached the last page?
- Are there any response headers for pagination metadata?
- What is the default page size?

**Suggestion**: Consider pagination standards:

- Offset/limit pattern
- Cursor-based pagination
- Link headers (RFC 5988)
- Total count in response

______________________________________________________________________

### 3. Error Response Format

**Current State**: `ProblemDetails` is referenced in 400 responses.

**Questions**:

- Is `ProblemDetails` following RFC 7807 (Problem Details for HTTP APIs)?
- Are there any error codes or categories we should handle?
- What does the structure look like?

**Suggestion**: Document the error response format with examples in the OpenAPI spec.

______________________________________________________________________

### 4. Date/Time Formats

**Observation**: Some endpoints (e.g., `DELETE /api/SalesOrders/Range`) use `fromDate`
and `toDate` parameters.

**Questions**:

- What date/time format is expected? (ISO 8601, Unix timestamp, etc.)
- Are times in UTC or local time?
- Are time zones supported?

**Suggestion**: Use OpenAPI's `format: date-time` with ISO 8601 examples in the spec.

______________________________________________________________________

### 5. API Versioning Strategy

**Current State**: API appears to use `/v1/` in some internal paths and has some
`/api/V2/` endpoints.

**Questions**:

- What is the versioning strategy?
- When would we use V2 endpoints vs V1?
- Are V1 endpoints deprecated?
- How are breaking changes communicated?

**Suggestion**: Document versioning policy and deprecation timeline.

______________________________________________________________________

## Additional Suggestions

### Rate Limiting

**Question**: Are there rate limits on the API?

**Suggestion**: If rate limiting exists, consider:

- Documenting limits in the API spec
- Including rate limit headers in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

______________________________________________________________________

### Webhooks

**Observation**: The spec includes an `InventoryCountWebHook` model.

**Questions**:

- Are webhooks available for other events?
- How do we register webhook URLs?
- What authentication is used for webhook callbacks?

**Suggestion**: Document webhook functionality if available.

______________________________________________________________________

### Field Validation

**Suggestion**: Consider adding validation constraints in the OpenAPI spec:

- `minLength` / `maxLength` for strings
- `pattern` for regex validation
- `minimum` / `maximum` for numbers
- `required` fields in request bodies

**Benefits**:

- Clients can validate before sending requests
- Better error messages
- Self-documenting constraints

______________________________________________________________________

### Nullable Arrays vs Optional Fields

**Current State**: Several models use `nullable: true` on array fields containing
complex objects:

- `OrderPlanResultsDto.results` - array of `SkuOptimizedResultsDto`
- `ProductsRequestDto.suppliers` - array of `ProductSupplier`
- `ProductsRequestDto.stockLocations` - array of `ProductLocation`
- `SalesOrderWithLineItemsRequestDto` - array of `SalesOrderRequestDto`
- `SetInventoryRequest.inventory` - array of `Inventory`
- `SquareWebHookObject` - array of `InventoryCountWebHook`

**Impact**: This pattern creates type checking complexity in strongly-typed languages,
requiring additional type casting to satisfy static analysis tools.

**Suggested Alternatives**:

1. **Use empty arrays instead of null** (Preferred):

   ```yaml
   # Instead of nullable array:
   suppliers:
     type: array
     items:
       $ref: '#/components/schemas/ProductSupplier'
     nullable: true

   # Use non-nullable array (return [] instead of null):
   suppliers:
     type: array
     items:
       $ref: '#/components/schemas/ProductSupplier'
   ```

1. **Make fields optional instead of nullable**:

   ```yaml
   # Omit the field entirely when no data exists
   suppliers:
     type: array
     items:
       $ref: '#/components/schemas/ProductSupplier'
   ```

**Benefits**:

- Simpler client code generation
- Better type safety in strongly-typed languages
- Follows JSON API best practices
- Reduces null-checking complexity for API consumers

______________________________________________________________________

### Nullable Date Fields Not Marked in Spec

**Issue Discovered**: 2025-10-31 **Status**: ✅ **FIXED** - The client regeneration
script now automatically adds `nullable: true` to fields that return `null`

**Previous Issue**: Several date/datetime fields in the API returned `null` values, but
the OpenAPI spec downloaded from StockTrim didn't always mark them as nullable. This
caused the generated Python client to fail with
`TypeError: object of type 'NoneType' has no len()` when trying to parse these fields.

**Solution**: The `regenerate_client.py` script now includes a post-processing step
(STEP 2.5) that automatically marks known nullable fields before generating the client
code. This ensures the generated code properly handles `null` values from the API.

**Implementation Details**:

- **Scalar/Date Fields**: Uses `nullable: true` (e.g., `orderDate`, `message`)
- **Object References**: Uses `allOf` with `nullable: true` due to OpenAPI 3.0
  limitation

OpenAPI 3.0 spec ignores `nullable: true` when it appears alongside `$ref`. For object
references (like `location`), the script uses this pattern:

```yaml
location:
  allOf:
    - $ref: '#/components/schemas/PurchaseOrderLocation'
  nullable: true
```

This correctly tells the code generator that the field can be either `null` or a
`PurchaseOrderLocation` object.

**Affected Models and Fields** (based on analysis of real API responses):

The StockTrim API returns `null` for many date/time and scalar fields. The downloaded
OpenAPI spec has most of these marked as nullable, but the regeneration script ensures
all known nullable fields are properly marked:

**PurchaseOrderResponseDto**:

- `message`: string (nullable)
- `orderDate`: date-time (nullable) ⚠️ CRITICAL
- `createdDate`: date-time (nullable)
- `fullyReceivedDate`: date-time (nullable)
- `externalId`: string (nullable)
- `referenceNumber`: string (nullable)
- `clientReferenceNumber`: string (nullable)
- `location`: object (nullable)

**PurchaseOrderSupplier** (nested in PurchaseOrderResponseDto):

- `supplierCode`: string (nullable)
- `supplierName`: string (nullable)

**PurchaseOrderLineItem**:

- `receivedDate`: date-time (nullable) ⚠️ CRITICAL
- `unitPrice`: number (nullable)

**Previous Impact (before fix)**:

- The Python client would crash when trying to parse purchase orders because
  `isoparse()` was called on `None` values
- Error: `TypeError: object of type 'NoneType' has no len()`

**Evidence from Real API Response** (2025-10-31):

```json
{
  "id": 31391357,
  "message": null,
  "orderDate": null,
  "createdDate": "2025-10-30T22:21:33.307",
  "fullyReceivedDate": null,
  "supplier": {
    "supplierCode": null,
    "supplierName": "Example Supplier"
  },
  "externalId": null,
  "referenceNumber": null,
  "clientReferenceNumber": "PO-00809",
  "location": null,
  "status": "Draft",
  "purchaseOrderLineItems": [
    {
      "productId": "33303389",
      "quantity": 3.0,
      "receivedDate": null,
      "unitPrice": 34.25
    }
  ]
}
```

**Note**: The `purchaseOrderLineItems` field is **NOT nullable** - it's always an array
in API responses (sometimes empty `[]`, never `null`). The spec correctly defines this
as a non-nullable array.

______________________________________________________________________

### POST Endpoints Support Upsert (Create OR Update)

**Issue Discovered**: 2025-11-01 **Status**: ✅ **DOCUMENTED** - POST endpoints use
upsert pattern

**Discovery**: Several POST endpoints in the StockTrim API support **upsert** behavior:

- POST **with** a reference identifier → Updates existing record (returns 200 OK)
- POST **without** a reference identifier → Creates new record (returns 201 Created)

**Affected Endpoints**:

- `POST /api/PurchaseOrders` - Uses `client_reference_number` as upsert key
- `POST /api/Products` - Uses `code` as upsert key

**Example** (Purchase Orders):

```http
POST /api/PurchaseOrders
{
  "client_reference_number": "PO-00810",  // Existing PO
  "supplier": {...},
  "purchase_order_line_items": [...]
}
→ Returns 200 OK (updated existing PO-00810)

POST /api/PurchaseOrders
{
  // No client_reference_number provided
  "supplier": {...},
  "purchase_order_line_items": [...]
}
→ Returns 201 Created (new PO created)
```

**OpenAPI Spec Issue**: The downloaded spec only documents 201 (Created) response,
missing the 200 (OK) response for updates. This causes generated clients to fail when
the API returns 200.

**Solution**: Our client regeneration script (`scripts/regenerate_client.py`) now
automatically adds 200 responses to upsert endpoints in STEP 2.6.

**Benefits of Upsert Pattern**:

- Simplifies client code (single endpoint for create/update)
- Idempotent operations
- Reduces need for separate PUT/PATCH endpoints

**Note**: This is non-standard REST behavior (POST typically only creates), but it's a
common pattern for APIs that prioritize simplicity over strict REST compliance.

______________________________________________________________________

### Order Date Field: Required for Updates, Optional in Responses

**Issue Discovered**: 2025-11-01 **Status**: ⚠️ **API LIMITATION** - Order date cannot
be cleared once set

**Discovery**: The `orderDate` field in Purchase Orders has asymmetric behavior:

- **GET responses**: `orderDate` can be `null` (we've observed this in production)
- **POST requests**: `orderDate` is **required** and cannot be set to `null`

**Impact**: Once a purchase order has an order date, it **cannot be cleared** via the
API. You can only:

1. Update it to a new date
1. Preserve the existing date (by omitting the field with `UNSET`)

**API Validation Error** when attempting to clear:

```http
POST /api/PurchaseOrders
{
  "client_reference_number": "PO-00810",
  "orderDate": null,  // ❌ Rejected!
  "supplier": {...},
  "purchase_order_line_items": [...]
}
→ 400 Bad Request: "The OrderDate field is required."
```

**Client Implementation**: Despite this limitation, we made `orderDate` nullable in
`PurchaseOrderRequestDto` to match the response schema and allow proper handling of null
values when reading POs. The field is optional (defaults to `UNSET`), allowing updates
that preserve the existing date.

**Workaround**: To modify a PO without changing its order date:

```python
update_request = PurchaseOrderRequestDto(
    supplier=original_po.supplier,
    purchase_order_line_items=updated_items,
    client_reference_number=original_po.client_reference_number,
    order_date=UNSET,  # Omit field - preserves existing date
)
```

**Recommendation for StockTrim**: Consider allowing `orderDate: null` in POST requests
to enable clearing dates, matching the behavior already supported in GET responses.

______________________________________________________________________

### DELETE Endpoint Returns 204 Instead of 200

**Issue Discovered**: 2025-11-04 **Status**: ✅ **PARTIALLY FIXED** - PurchaseOrders
updated, others still use 200

**Discovery**: The StockTrim API was updated to return `204 No Content` for DELETE
operations on Purchase Orders, but the OpenAPI spec still documents `200 OK`.

**Affected Endpoints**:

- `DELETE /api/PurchaseOrders` - ✅ Returns 204 No Content (updated by Joel on
  2025-11-04)
- `DELETE /api/Products` - ⚠️ Still returns 200 OK (takes 5+ seconds to complete)
- `DELETE /api/SalesOrders` - Status unknown
- `DELETE /api/SalesOrders/All` - Status unknown
- `DELETE /api/SalesOrders/Range` - Status unknown
- `DELETE /api/SalesOrdersLocation` - Status unknown
- `DELETE /api/Suppliers` - Status unknown
- `DELETE /api/boms` - Status unknown (spec says 201 which is incorrect for DELETE)

**REST Best Practice**: DELETE operations should return `204 No Content` when successful
and no response body is returned.

**Impact Before Fix**: The Python client would crash on `DELETE /api/PurchaseOrders`
because it expected response data for status 200, but the API returned empty body with
204\.

**Solution**: Our client regeneration script now automatically updates DELETE
/api/PurchaseOrders to expect 204 in STEP 2.8.

**Recommendation for StockTrim**: Consider migrating all DELETE endpoints to return 204
No Content for consistency and REST compliance.

______________________________________________________________________

### Purchase Order Status Returns Integer Instead of String

**Issue Discovered**: 2025-11-04 **Status**: ✅ **DOCUMENTED** - Spec updated to match
API behavior

**Discovery**: The `PurchaseOrderStatusDto` enum in the OpenAPI spec defines status as a
string enum with values `["Draft", "Approved", "Sent", "Received"]`, but the actual API
returns integer values `[0, 1, 2, 3]`.

**Mapping**:

- `0` = Draft
- `1` = Approved
- `2` = Sent
- `3` = Received

**Impact Before Fix**: The generated Python client would crash when parsing purchase
order responses with:

```
ValueError: 0 is not a valid PurchaseOrderStatusDto
```

**Example API Response**:

```json
{
  "id": 12347,
  "clientReferenceNumber": "PO-TEST-006",
  "status": 0,  // Integer value, not "Draft"
  "orderDate": "2025-01-01T00:00:00Z",
  ...
}
```

**OpenAPI Spec (Current - Incorrect)**:

```yaml
PurchaseOrderStatusDto:
  type: string
  enum:
    - Draft
    - Approved
    - Sent
    - Received
```

**Solution**: Our client regeneration script now automatically converts the enum to use
integer type with `x-enum-varnames` for human-readable names in STEP 2.7:

```yaml
PurchaseOrderStatusDto:
  type: integer
  enum: [0, 1, 2, 3]
  x-enum-varnames: [Draft, Approved, Sent, Received]
  description: Purchase order status (0=Draft, 1=Approved, 2=Sent, 3=Received)
```

The `x-enum-varnames` extension tells code generators to use the provided names for each
enum value. The mapping is positional: the first value in `enum` (0) gets the first name
in `x-enum-varnames` ("Draft"), the second value (1) gets the second name ("Approved"),
etc.

This generates a proper Python `IntEnum`:

```python
class PurchaseOrderStatusDto(IntEnum):
    DRAFT = 0      # "Draft" from x-enum-varnames[0] → DRAFT = enum[0]
    APPROVED = 1   # "Approved" from x-enum-varnames[1] → APPROVED = enum[1]
    SENT = 2
    RECEIVED = 3
```

**Recommendation for StockTrim**: Update the OpenAPI spec to use integer type with
x-enum-varnames to match actual API behavior, or update the API to return string values
to match the current spec.

______________________________________________________________________

### Products Endpoint Returns 404 for Query Parameter Filtering

**Issue Discovered**: 2025-11-11 **Status**: ⚠️ **NON-STANDARD BEHAVIOR** - Endpoint
returns 404 for "no results"

**Discovery**: The `GET /api/Products` endpoint returns `404 Not Found` when query
parameter filtering produces no results, rather than the more conventional `200 OK` with
an empty array.

**Test Results**:

| Query                                              | Status | Result              |
| -------------------------------------------------- | ------ | ------------------- |
| `GET /api/Products`                                | 200    | List of 50 products |
| `GET /api/Products?code=14851399` (exact match)    | 200    | List with 1 product |
| `GET /api/Products?code=NONEXISTENT`               | 404    | Empty response      |
| `GET /api/Products?code=148` (prefix of real code) | 404    | Empty response      |

**Why This Is Non-Standard**:

In REST conventions, HTTP 404 indicates the **resource path itself doesn't exist**.
Since `/api/Products` is a valid endpoint, the appropriate response for "no matching
products" should be:

- Status: `200 OK`
- Body: `[]` (empty array)

The 404 status code is typically reserved for:

- Missing resource IDs in the path: `GET /api/Products/999999` → 404
- Invalid endpoint paths: `GET /api/InvalidEndpoint` → 404

**Current Behavior**: Query parameter filtering returns 404 for "no results":

```http
GET /api/Products?code=NONEXISTENT
→ 404 Not Found
```

**Expected REST Behavior**: Query parameter filtering returns empty list for "no
results":

```http
GET /api/Products?code=NONEXISTENT
→ 200 OK
   []
```

**Client Impact**: This behavior creates ambiguity:

- Is 404 a "no results" response? (current interpretation)
- Or is it an actual error (malformed request, endpoint doesn't exist)?

We've worked around this by treating 404 as "no results found" in our helper methods,
but this required special-case handling.

**Additional Discovery**: The `code` query parameter only supports **exact match**, not
prefix search:

- `code=14851399` → Returns matching product
- `code=148` (prefix) → Returns 404, not products starting with "148"

This makes the parameter less useful for search functionality, as it requires knowing
the exact product code.

**Recommendation for StockTrim**: Consider either:

1. Return `200 OK` with empty array when query filters produce no results (preferred)
1. Document this 404 behavior explicitly in the API specification if it's intentional
1. Add a separate search/filter endpoint that supports prefix matching and returns 200 +
   empty array for no results

______________________________________________________________________

### v1 vs v2 Endpoint Availability Issues

**Issue Discovered**: 2025-11-13 **Status**: 🔴 **CRITICAL** - Multiple endpoints return
404 despite being in OpenAPI spec

**Discovery**: Testing against production StockTrim API revealed that several v1
endpoints return 404 Not Found, while v2 alternatives (where they exist) work correctly.
This creates significant confusion as the OpenAPI spec includes both versions without
clear deprecation notices.

#### Purchase Orders: v1 Returns 404, v2 Works

**Affected Endpoints**:

- ❌ `GET /api/PurchaseOrders` - Returns 404
- ✅ `GET /api/V2/PurchaseOrders` - Returns 200 with data

**Test Results**:

```bash
# v1 endpoint - 404 Not Found
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    https://api.stocktrim.com/api/PurchaseOrders
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.4","title":"Not Found","status":404}

# v2 endpoint - 200 OK
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    https://api.stocktrim.com/api/v2/PurchaseOrders
[... returns 10 purchase orders ...]
```

**OpenAPI Spec Endpoints**:

Both versions are defined in the spec without deprecation notices:

- `/api/PurchaseOrders` (GET, POST, DELETE) - Lines 528-605
- `/api/V2/PurchaseOrders` (GET with pagination) - Lines 669-707
- `/api/V2/PurchaseOrders/{referenceNumber}` (GET by ID) - Lines 606-627
- `/api/V2/PurchaseOrders/OrderPlan` (POST generate from plan) - Lines 632-667

**Impact**:

- Client code using v1 endpoints fails with 404 errors
- MCP tools non-functional (`list_purchase_orders`, `get_purchase_order`)
- Workflow tools depending on purchase orders fail
- No clear migration path without testing both versions

#### Sales Orders: No Working GET Endpoint

**Affected Endpoint**:

- ❌ `GET /api/SalesOrders` - Returns 404 (with or without `productId` parameter)
- ❌ No v2 alternative exists

**Test Results**:

```bash
# Without productId - 404
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    https://api.stocktrim.com/api/SalesOrders
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.4","title":"Not Found","status":404}

# With numeric productId - 404
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    "https://api.stocktrim.com/api/SalesOrders?productId=35509896"
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.4","title":"Not Found","status":404}

# With code-based productId - Also 404
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    "https://api.stocktrim.com/api/SalesOrders?productId=TEST-DEL-20251104142211"
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.4","title":"Not Found","status":404}
```

**Note**: StockTrim's `productId` field can be either a numeric internal ID (e.g.,
"35509896") or the product code/SKU (e.g., "TEST-DEL-20251104142211"). Both formats were
tested and both return 404.

**OpenAPI Spec Definition**:

The spec defines GET with optional `productId` parameter (Lines 723-748):

```yaml
/api/SalesOrders:
  get:
    parameters:
      - name: productId
        in: query
        schema:
          type: string
```

**Impact**:

- Cannot list sales orders via API
- Cannot filter sales orders by product
- Cannot verify sales order creation
- Cannot query historical sales order data
- MCP tools `get_sales_orders` and `list_sales_orders` non-functional

**Questions**:

1. Is sales order querying intentionally disabled?
1. Is there an alternative endpoint we should use?
1. Will a v2 sales orders GET endpoint be added?

#### Locations: No Listing Endpoint

**Affected Endpoints**:

- ❌ `GET /api/Locations` - Returns 404
- ❌ `GET /api/V2/Locations` - Not defined (v2 only has POST)

**Test Results**:

```bash
# v1 GET - 404
$ curl -H "api-auth-id: <id>" -H "api-auth-signature: <sig>" \
    https://api.stocktrim.com/api/Locations
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.4","title":"Not Found","status":404}
```

**OpenAPI Spec**:

- `/api/Locations` (Lines 299-357) - Defines GET with optional `code` parameter, but
  returns 404
- `/api/V2/Locations` (Lines 358-390) - Only POST defined (create/update), no GET

**Impact**:

- Cannot list all locations programmatically
- MCP tool `list_locations` non-functional
- Multi-location workflows cannot enumerate locations
- Must know location codes beforehand

**Workaround**: The GET endpoint accepts a `code` parameter to retrieve a specific
location, but this requires knowing the code exists first.

#### Working Endpoints (Baseline for Comparison)

For reference, these v1 endpoints work correctly:

| Endpoint           | Status | Notes              |
| ------------------ | ------ | ------------------ |
| `/api/Products`    | ✅ 200 | Returns 50 items   |
| `/api/Customers`   | ✅ 200 | Returns 14,766     |
| `/api/Suppliers`   | ✅ 200 | Works (null codes) |
| `/api/Inventory`   | ✅ 200 | POST works         |
| \`/api/RunForecast | ✅ 201 | POST works         |

#### Endpoint Status Summary

| Endpoint                       | Version | Method | Status | Notes                       |
| ------------------------------ | ------- | ------ | ------ | --------------------------- |
| `/api/Products`                | v1      | GET    | ✅ 200 | 50 products                 |
| `/api/Customers`               | v1      | GET    | ✅ 200 | 14,766 customers            |
| `/api/Suppliers`               | v1      | GET    | ✅ 200 | Works (some null codes)     |
| `/api/PurchaseOrders`          | v1      | GET    | ❌ 404 | Deprecated - use v2         |
| `/api/V2/PurchaseOrders`       | v2      | GET    | ✅ 200 | 10 orders, pagination works |
| `/api/SalesOrders`             | v1      | GET    | ❌ 404 | No alternative exists       |
| `/api/Locations`               | v1      | GET    | ❌ 404 | No alternative exists       |
| `/api/V2/Locations`            | v2      | POST   | ✅ 201 | Create/update only          |
| `/api/SalesOrdersLocation`     | v1      | GET    | ❌ 405 | Method not allowed          |
| `/api/SalesOrdersLocation`     | v1      | DELETE | ✅ 200 | Tested via spec             |
| \`/api/RunForecastCalculations | v1      | POST   | ✅ 201 | Tested via MCP              |

#### Recommendations

**Immediate (Critical)**:

1. **Document v1/v2 strategy**: Add clear deprecation notices to v1 endpoints in OpenAPI
   spec
1. **Fix or remove broken endpoints**: Either make v1 endpoints work or remove from spec
1. **Add v2 alternatives**: Provide v2 GET endpoints for Sales Orders and Locations
1. **Migration guide**: Document how to migrate from v1 to v2 endpoints

**Short-term (Important)**:

1. **HTTP status codes**: Return `410 Gone` instead of `404 Not Found` for deprecated
   endpoints
1. **API versioning documentation**: Publish clear versioning policy and deprecation
   timeline
1. **Endpoint consistency**: All entity types should have similar v2
   list/get/create/delete operations

**Medium-term (Enhancement)**:

1. **Unified v2 API**: Complete v2 API with consistent patterns across all entities
1. **Deprecation headers**: Add `Deprecation` and `Sunset` headers to v1 responses
1. **Link headers**: Include `Link: <v2-url>; rel="successor-version"` on v1 endpoints

#### Client Workarounds

Our client library works around these issues:

1. **Purchase Orders**: Helper methods updated to use v2 endpoints
1. **Sales Orders**: Document as non-functional, return empty arrays
1. **Locations**: Document limitation, require codes to be known beforehand
1. **404 handling**: Special-case 404 responses to distinguish "not found" from "no
   results"

#### Questions for StockTrim Team

1. **What is the timeline for deprecating v1 endpoints?**
1. **Will v2 endpoints be added for Sales Orders and Locations?**
1. **Is the 404 behavior on v1 endpoints intentional or a configuration issue?**
1. **Should clients always use v2 when available?**
1. **Are there other v1 endpoints that are deprecated but not documented?**

______________________________________________________________________

## Closing Notes

Thank you for providing a public API! These suggestions come from a place of wanting to
help make the API even better for all developers using it.

We're happy to:

- Discuss any of these points in detail
- Provide code examples or proof-of-concepts
- Test updated specifications
- Contribute to documentation

**Contact**: Feel free to reach out if you'd like to discuss any of this feedback.

______________________________________________________________________

**Document Maintenance**: This document will be updated as we discover more insights
while using the API.
