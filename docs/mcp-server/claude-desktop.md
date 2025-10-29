# Claude Desktop Setup

Configure Claude Desktop to use the StockTrim MCP Server.

## Prerequisites

- Claude Desktop installed
- `stocktrim-mcp-server` package installed
- StockTrim API credentials

## Configuration Steps

### 1. Locate Claude Desktop Config

The configuration file is located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add StockTrim MCP Server

Edit the configuration file and add the StockTrim server:

```json
{
  "mcpServers": {
    "stocktrim": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project",
        "run",
        "stocktrim-mcp-server"
      ],
      "env": {
        "STOCKTRIM_API_AUTH_ID": "your_tenant_id",
        "STOCKTRIM_API_AUTH_SIGNATURE": "your_tenant_name"
      }
    }
  }
}
```

### 3. Alternative: Using pip

If you installed with pip instead of uv:

```json
{
  "mcpServers": {
    "stocktrim": {
      "command": "python",
      "args": ["-m", "stocktrim_mcp_server"],
      "env": {
        "STOCKTRIM_API_AUTH_ID": "your_tenant_id",
        "STOCKTRIM_API_AUTH_SIGNATURE": "your_tenant_name"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

## Verification

Once configured, you should see the StockTrim tools available in Claude Desktop. Try asking:

> "List all products in StockTrim"

## Troubleshooting

### Server Not Appearing

1. Check the configuration file syntax (valid JSON)
2. Verify the path to your project
3. Ensure credentials are correct
4. Check Claude Desktop logs

### Connection Errors

1. Verify your StockTrim credentials
2. Check network connectivity
3. Ensure the base URL is correct

### Permission Issues

Make sure the `stocktrim-mcp-server` command is executable:

```bash
which stocktrim-mcp-server
# Should show the path to the executable
```

## Next Steps

- [Available Tools](tools.md) - Explore what you can do with the MCP server
- [Overview](overview.md) - Learn more about the MCP server architecture
