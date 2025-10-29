# StockTrim API Feedback

This document tracks issues and feedback about the StockTrim API itself (not this client library).

## How to Report Issues

For issues with the StockTrim API:

1. Contact StockTrim support directly
2. Document the issue in this repository for tracking
3. We'll update the client when the API is fixed

## Known API Issues

### Documentation

- Some endpoints lack complete documentation
- Response formats not always consistent with spec
- Some error responses don't include details

### Consistency

- Mix of DTO and integration models can be confusing
- Some endpoints return single items, others return arrays
- Naming conventions vary between endpoints

## Feature Requests

### Nice to Have

- Pagination for large result sets
- Rate limiting headers
- Webhook support for real-time updates
- Bulk operations for better performance
- GraphQL API for flexible queries

### API Improvements

- Consistent error response format
- More detailed error messages
- Request ID tracking
- API versioning strategy

## Providing Feedback

When reporting API issues:

1. **Be specific**: Include endpoint, request, response
2. **Show examples**: Provide actual requests/responses
3. **Suggest solutions**: How would you like it to work?

### Example

**Issue**: Product endpoint returns 404 for empty results

**Current behavior**:
```
GET /api/products
Response: 404 Not Found
```

**Expected behavior**:
```
GET /api/products
Response: 200 OK
Body: []
```

**Workaround**: Client handles both 200 and 404 as valid empty responses.

## Contributing

If you find an API issue:

1. Open an issue in this repository
2. Tag it with `api-issue`
3. Include reproduction steps
4. Note any client-side workarounds

## Contact

- **StockTrim Support**: Contact through your StockTrim account
- **Client Issues**: https://github.com/dougborg/stocktrim-openapi-client/issues
