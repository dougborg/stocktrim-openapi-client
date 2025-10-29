# Installation

## Requirements

- Python 3.11 or higher
- pip or uv package manager

## Install the Client Library

### Using pip

```bash
pip install stocktrim-openapi-client
```

### Using uv

```bash
uv pip install stocktrim-openapi-client
```

## Install the MCP Server

If you want to use the Model Context Protocol server for AI integration:

```bash
pip install stocktrim-mcp-server
```

## Verify Installation

Test that the packages are installed correctly:

```python
import stocktrim_public_api_client
print(stocktrim_public_api_client.__version__)
```

## Development Installation

If you want to contribute to the project, clone the repository and install in development mode:

```bash
git clone https://github.com/dougborg/stocktrim-openapi-client.git
cd stocktrim-openapi-client

# Install uv if you don't have it
pip install uv

# Sync all dependencies
uv sync --all-extras
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started with basic usage
- [Configuration](configuration.md) - Learn how to configure the client
