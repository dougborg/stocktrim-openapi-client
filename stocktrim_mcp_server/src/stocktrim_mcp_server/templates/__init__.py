"""Markdown template loaders for tool responses.

- :func:`render_template` (Jinja2, ``.md.j2``) — use for new templates.
- :func:`format_template` / :func:`load_template` (``str.format``, ``.md``) —
  legacy path; kept so existing forecast templates render unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

TEMPLATE_DIR = Path(__file__).parent

# StrictUndefined: typos fail loudly instead of rendering as empty strings.
_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    undefined=StrictUndefined,
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def _pluralize(n: int, singular: str = "", plural: str = "s") -> str:
    """Jinja filter: ``{{ 3 | pluralize }}`` → ``"s"``, ``{{ 1 | pluralize }}`` → ``""``."""
    return singular if n == 1 else plural


_jinja_env.filters["pluralize"] = _pluralize


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


def render_template(template_path: str, **context: Any) -> str:
    """Render a Jinja2 markdown template (use for new ``ToolResult`` outputs).

    Templates live in a domain-grouped layout under ``templates/``::

        templates / workflows / urgent_orders / review.md.j2
        templates / foundation / products / get.md.j2

    Args:
        template_path: Path to the template, relative to ``templates/``,
            without the ``.md.j2`` suffix. For example, pass
            ``"workflows/urgent_orders/review"`` to render
            ``templates/workflows/urgent_orders/review.md.j2``.
        **context: Variables made available inside the template.

    Returns:
        Rendered template content.

    Raises:
        jinja2.TemplateNotFound: If the template doesn't exist.
        jinja2.UndefinedError: If the template references a variable that
            wasn't supplied (StrictUndefined).
    """
    template = _jinja_env.get_template(f"{template_path}.md.j2")
    return template.render(**context)
