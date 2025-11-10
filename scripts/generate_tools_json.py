#!/usr/bin/env python3
"""Generate tools.json for Docker MCP Registry from MCP server tools.

This script introspects the registered MCP tools and generates a tools.json
file suitable for the Docker MCP Registry submission. This ensures the tools
list stays in sync with the actual tool implementations.

Usage:
    python scripts/generate_tools_json.py > /path/to/tools.json
    python scripts/generate_tools_json.py --output /path/to/tools.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import the server module
sys.path.insert(0, str(Path(__file__).parent.parent / "stocktrim_mcp_server" / "src"))

from stocktrim_mcp_server.server import mcp


def extract_tool_info():
    """Extract tool information from registered MCP tools.

    Returns:
        List of tool dictionaries with name and description.
    """
    tools = []

    # Access the tool manager directly
    tool_manager = mcp._tool_manager

    # Iterate through registered tools
    for name, tool_info in tool_manager._tools.items():
        # Get description from the tool's schema if available
        description = ""
        if hasattr(tool_info, "description") and tool_info.description:
            description = tool_info.description
        elif hasattr(tool_info, "fn") and tool_info.fn.__doc__:
            # Extract first non-empty line from docstring
            lines = [
                line.strip()
                for line in tool_info.fn.__doc__.split("\n")
                if line.strip()
            ]
            description = lines[0] if lines else f"Tool: {name}"
        else:
            description = f"Tool: {name}"

        tools.append({"name": name, "description": description})

    # Sort alphabetically by name
    tools.sort(key=lambda x: x["name"])

    return tools


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate tools.json for Docker MCP Registry"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--pretty",
        "-p",
        action="store_true",
        help="Pretty-print JSON output with indentation",
    )

    args = parser.parse_args()

    # Extract tool information
    tools = extract_tool_info()

    # Format JSON
    if args.pretty:
        json_output = json.dumps(tools, indent=2) + "\n"
    else:
        json_output = json.dumps(tools) + "\n"

    # Write output
    if args.output:
        args.output.write_text(json_output)
        print(
            f"Generated tools.json with {len(tools)} tools → {args.output}",
            file=sys.stderr,
        )
    else:
        print(json_output, end="")


if __name__ == "__main__":
    main()
