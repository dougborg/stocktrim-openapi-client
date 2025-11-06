"""Template loader for markdown response templates.

This module provides utilities for loading and formatting markdown templates
for workflow tool responses.
"""

from pathlib import Path

# Template directory
TEMPLATE_DIR = Path(__file__).parent


def load_template(template_name: str) -> str:
    """Load a markdown template by name.

    Args:
        template_name: Name of the template file (without .md extension)

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template_path = TEMPLATE_DIR / f"{template_name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return template_path.read_text()


def format_template(template_name: str, **kwargs) -> str:
    """Load and format a markdown template.

    Args:
        template_name: Name of the template file (without .md extension)
        **kwargs: Format variables to substitute in the template

    Returns:
        Formatted template content

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template = load_template(template_name)
    return template.format(**kwargs)
