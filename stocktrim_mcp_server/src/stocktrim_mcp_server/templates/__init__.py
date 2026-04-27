"""Template loader for markdown response templates.

This module provides utilities for loading and formatting markdown templates
for workflow tool responses.

Two engines are supported during the v3 migration:

- ``format_template`` / ``load_template`` use Python's :func:`str.format` and
  read ``.md`` files. They are the legacy path used by the early forecast
  templates and remain in place so older callers keep working.
- ``render_template`` uses Jinja2 and reads ``.md.j2`` files. New templates
  authored as part of the ``ToolResult`` migration (#149) use this path —
  iteration, conditionals, and filters belong here.

A future PR will migrate the legacy ``.md`` templates onto Jinja2 once every
caller is happy with the new pattern. Until then, both engines coexist.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

# Template directory
TEMPLATE_DIR = Path(__file__).parent

# Jinja2 environment for ``.md.j2`` templates. ``StrictUndefined`` makes typos
# fail loudly during render rather than silently emitting empty strings.
_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    undefined=StrictUndefined,
    autoescape=select_autoescape(default=False),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def load_template(template_name: str) -> str:
    """Load a markdown template by name (legacy str.format engine).

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
    """Load and format a markdown template using :func:`str.format` (legacy engine).

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


def render_template(template_name: str, **context: Any) -> str:
    """Render a Jinja2 markdown template (use for new ``ToolResult`` outputs).

    Args:
        template_name: Name of the template file. ``".md.j2"`` is appended
            automatically — pass ``"urgent_orders_review"`` to render
            ``urgent_orders_review.md.j2``.
        **context: Variables made available inside the template.

    Returns:
        Rendered template content.

    Raises:
        jinja2.TemplateNotFound: If the template doesn't exist.
        jinja2.UndefinedError: If the template references a variable that
            wasn't supplied (StrictUndefined).
    """
    template = _jinja_env.get_template(f"{template_name}.md.j2")
    return template.render(**context)
