# MCP Server Installation

The StockTrim MCP Server enables AI agents like Claude Desktop to interact with the StockTrim API.

## Requirements

- Python 3.11 or higher
- Claude Desktop or another MCP-compatible client
- StockTrim API credentials

## Installation

### Via pip

```bash
pip install stocktrim-mcp-server
```

### Via uv (Recommended)

```bash
uv pip install stocktrim-mcp-server
```

## Configuration

### Environment Variables

Create a `.env` file with your StockTrim credentials:

```bash
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
STOCKTRIM_BASE_URL=https://api.stocktrim.com  # optional
```

## Next Steps

- [Claude Desktop Setup](claude-desktop.md) - Configure Claude Desktop
- [Available Tools](tools.md) - Explore MCP tools
- [Overview](overview.md) - Learn more about the MCP server
