"""Markdown template loaders for forecast management tool responses.

These ``str.format``-engine ``.md`` templates are still used by the
forecast workflow tools (``forecasts_update_and_monitor``,
``forecasts_get_for_products``) which return formatted strings rather
than typed responses. Other tools should use the JSON-content pattern in
:mod:`stocktrim_mcp_server.tools.tool_result_utils` (``make_json_result``)
— see issue #179 for the migration rationale.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

TEMPLATE_DIR = Path(__file__).parent


def load_template(template_name: str) -> str:
    """Load a markdown template by name.

    Args:
        template_name: Name of the template file (without ``.md`` extension)

    Returns:
        Template content as string.

    Raises:
        FileNotFoundError: If the template doesn't exist.
    """
    template_path = TEMPLATE_DIR / f"{template_name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return template_path.read_text()


def format_template(template_name: str, **kwargs: Any) -> str:
    """Load and format a markdown template using :func:`str.format`.

    Args:
        template_name: Name of the template file (without ``.md`` extension)
        **kwargs: Format variables to substitute into the template.

    Returns:
        Formatted template content.

    Raises:
        FileNotFoundError: If the template doesn't exist.
    """
    template = load_template(template_name)
    return template.format(**kwargs)
