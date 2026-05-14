#!/usr/bin/env python3
"""Build the StockTrim MCP server as an MCP Bundle (``.mcpb``).

The MCP Bundle format (formerly DXT) is Claude Desktop's one-click install
package for local MCP servers. See https://github.com/anthropics/mcpb.

Pipeline:

1. Read the package version from ``stocktrim_mcp_server/pyproject.toml``.
2. Stage a self-contained bundle directory under ``build/mcpb/`` containing:

   - ``manifest.json``           — derived from
     ``stocktrim_mcp_server/mcpb/manifest.template.json`` with ``__VERSION__``
     substituted.
   - ``pyproject.toml``          — derived from
     ``stocktrim_mcp_server/mcpb/pyproject.template.toml`` with ``__VERSION__``
     substituted; production deps mirrored from the package's own
     ``pyproject.toml`` minus the workspace source ref. Mirroring is
     verified — drift between the two files fails the build loudly.
   - ``.mcpbignore``             — copied as-is.
   - ``src/stocktrim_mcp_server/`` — copied from
     ``stocktrim_mcp_server/src/stocktrim_mcp_server/``.
   - ``README.md``               — copied from the package's own README.

3. Validate ``manifest.json`` against the MCPB schema via ``mcpb validate``.
4. Run ``mcpb pack build/mcpb dist/stocktrim-mcp-server-<version>.mcpb`` to
   produce the final ``.mcpb`` artifact.

Requires the ``mcpb`` CLI on PATH (``npm install -g @anthropic-ai/mcpb``).
Outputs the artifact path on stdout — release CI uses that as the upload path.

Env: ``MCPB_SKIP_PACK=1`` stages the bundle but skips ``mcpb pack`` (handy when
the CLI isn't installed locally — CI installs it on demand).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "stocktrim_mcp_server"
PKG_PYPROJECT = PKG_ROOT / "pyproject.toml"
PKG_SRC = PKG_ROOT / "src" / "stocktrim_mcp_server"
PKG_README = PKG_ROOT / "README.md"

MCPB_DIR = PKG_ROOT / "mcpb"
MANIFEST_TEMPLATE = MCPB_DIR / "manifest.template.json"
PYPROJECT_TEMPLATE = MCPB_DIR / "pyproject.template.toml"
MCPBIGNORE = MCPB_DIR / ".mcpbignore"

BUILD_DIR = REPO_ROOT / "build" / "mcpb"
DIST_DIR = REPO_ROOT / "dist"

VERSION_PLACEHOLDER = "__VERSION__"
CLIENT_DEP_PLACEHOLDER = "__STOCKTRIM_CLIENT_DEP__"
CLIENT_PKG_NAME = "stocktrim-openapi-client"


def read_pkg_pyproject() -> dict[str, Any]:
    with PKG_PYPROJECT.open("rb") as f:
        return tomllib.load(f)


def get_pkg_version(pyproject: dict[str, Any]) -> str:
    version = pyproject.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise RuntimeError(f"Could not read [project.version] from {PKG_PYPROJECT}")
    return version


def get_client_dep(pyproject: dict[str, Any]) -> str:
    """Return the package's ``stocktrim-openapi-client`` requirement string.

    On a real MCP release the workflow rewrites this to
    ``stocktrim-openapi-client==<version>`` before tagging, so the bundle must
    carry the same pin to keep ``verify_dep_mirror`` honest. Returning the
    raw requirement string (rather than just a version) keeps the substitution
    transparent — whatever the package depends on, the bundle depends on.
    """
    for dep in pyproject.get("project", {}).get("dependencies", []):
        if (
            dep.split("[", 1)[0]
            .split("=", 1)[0]
            .split("<", 1)[0]
            .split(">", 1)[0]
            .strip()
            == CLIENT_PKG_NAME
        ):
            return dep
    raise RuntimeError(
        f"Could not find a `{CLIENT_PKG_NAME}` requirement in {PKG_PYPROJECT}"
    )


def substitute(template: str, replacements: dict[str, str]) -> str:
    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    return result


def verify_dep_mirror(pkg_pyproject: dict[str, Any]) -> None:
    """Fail loudly if the bundle pyproject's deps drift from the package's.

    The bundle template hand-copies the production deps so that we can omit the
    workspace ``[tool.uv.sources]`` ref (which only resolves inside the
    monorepo). When new deps are added to the package, the template must be
    updated to match — otherwise the bundle would silently miss them at
    runtime.

    The ``stocktrim-openapi-client`` line is special-cased: the template carries
    a placeholder that the build script substitutes at pack time, so the mirror
    check parses the template *after* substitution. This keeps the check valid
    when the release workflow pins the client dep to an exact version.
    """
    client_dep = get_client_dep(pkg_pyproject)
    substituted = substitute(
        PYPROJECT_TEMPLATE.read_text(encoding="utf-8"),
        {CLIENT_DEP_PLACEHOLDER: client_dep},
    )
    bundle_pyproject = tomllib.loads(substituted)

    pkg_deps = set(pkg_pyproject.get("project", {}).get("dependencies", []))
    bundle_deps = set(bundle_pyproject.get("project", {}).get("dependencies", []))

    missing_from_bundle = pkg_deps - bundle_deps
    extra_in_bundle = bundle_deps - pkg_deps

    if missing_from_bundle or extra_in_bundle:
        msg = ["Bundle pyproject.template.toml is out of sync with the package's."]
        if missing_from_bundle:
            msg.append("  Missing from bundle (add to template):")
            msg.extend(f"    - {dep}" for dep in sorted(missing_from_bundle))
        if extra_in_bundle:
            msg.append("  Extra in bundle (remove from template):")
            msg.extend(f"    - {dep}" for dep in sorted(extra_in_bundle))
        raise RuntimeError("\n".join(msg))


def _write_substituted(src: Path, dest: Path, replacements: dict[str, str]) -> None:
    # Force UTF-8 + LF on read and write — templates contain non-ASCII chars
    # (em-dash, arrow). Default encoding is locale-dependent; on a non-UTF-8
    # locale (Windows ``cp1252``) the round-trip silently corrupts manifest
    # text and the bundle ships with garbled metadata.
    dest.write_text(
        substitute(src.read_text(encoding="utf-8"), replacements),
        encoding="utf-8",
        newline="\n",
    )


def stage_bundle(version: str, client_dep: str) -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)

    _write_substituted(
        MANIFEST_TEMPLATE,
        BUILD_DIR / "manifest.json",
        {VERSION_PLACEHOLDER: version},
    )
    _write_substituted(
        PYPROJECT_TEMPLATE,
        BUILD_DIR / "pyproject.toml",
        {VERSION_PLACEHOLDER: version, CLIENT_DEP_PLACEHOLDER: client_dep},
    )
    shutil.copy2(MCPBIGNORE, BUILD_DIR / ".mcpbignore")

    src_dest = BUILD_DIR / "src" / "stocktrim_mcp_server"
    shutil.copytree(
        PKG_SRC,
        src_dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    shutil.copy2(PKG_README, BUILD_DIR / "README.md")


def run_mcpb_validate() -> None:
    subprocess.run(
        ["mcpb", "validate", str(BUILD_DIR / "manifest.json")],
        check=True,
    )


def run_mcpb_pack(version: str) -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    artifact = DIST_DIR / f"stocktrim-mcp-server-{version}.mcpb"
    artifact.unlink(missing_ok=True)
    subprocess.run(
        ["mcpb", "pack", str(BUILD_DIR), str(artifact)],
        check=True,
    )
    return artifact


def main() -> int:
    pyproject = read_pkg_pyproject()
    version = get_pkg_version(pyproject)
    client_dep = get_client_dep(pyproject)
    verify_dep_mirror(pyproject)
    stage_bundle(version, client_dep)

    if os.environ.get("MCPB_SKIP_PACK") == "1":
        print(BUILD_DIR, file=sys.stdout)
        return 0

    run_mcpb_validate()
    artifact = run_mcpb_pack(version)
    print(artifact, file=sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
