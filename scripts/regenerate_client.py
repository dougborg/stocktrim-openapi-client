#!/usr/bin/env python3
"""
Script to regenerate the StockTrim API client from the OpenAPI specification.

This script:
1. Downloads the latest OpenAPI spec from StockTrim
2. Fixes authentication in the spec (converts header params to securitySchemes)
3. Validates the specification using multiple validators
4. Generates a new Python client using openapi-python-client
5. Performs post-processing:
   - Renames types.py to client_types.py
   - Fixes all imports to use client_types
   - Modernizes Union types to use | syntax
   - Fixes RST docstring formatting
6. Runs ruff auto-fixes
7. Validates the generated code with tests
"""

import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
import yaml
from openapi_spec_validator import validate as validate_spec

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SPEC_URL = "https://api.stocktrim.com/swagger/v1/swagger.yaml"
SPEC_FILE = PROJECT_ROOT / "stocktrim-openapi.yaml"
CLIENT_PACKAGE = "stocktrim_public_api_client"
CLIENT_DIR = PROJECT_ROOT / CLIENT_PACKAGE


def download_openapi_spec() -> str:
    """Download the OpenAPI specification from StockTrim."""
    logger.info(f"Downloading OpenAPI spec from {SPEC_URL}")

    try:
        response = httpx.get(SPEC_URL, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        spec_content = response.text
        logger.info("✅ Successfully downloaded OpenAPI specification")
        return spec_content
    except Exception as e:
        logger.error(f"❌ Failed to download OpenAPI spec: {e}")
        sys.exit(1)


def save_spec_file(spec_content: str) -> None:
    """Save the specification as YAML file."""
    logger.info(f"Saving OpenAPI spec to {SPEC_FILE}")

    try:
        with open(SPEC_FILE, "w") as f:
            f.write(spec_content)
        logger.info("✅ Saved OpenAPI specification")
    except Exception as e:
        logger.error(f"❌ Failed to save spec file: {e}")
        sys.exit(1)


def fix_auth_in_spec(spec_path: Path) -> bool:
    """Convert auth header parameters to proper security scheme.

    StockTrim's spec defines api-auth-id and api-auth-signature as required
    header parameters on every endpoint. This converts them to a proper
    securitySchemes definition, which allows openapi-python-client to handle
    auth correctly without generating redundant parameters.
    """
    logger.info("Converting auth headers to security scheme")

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        # Add security scheme to components
        if "components" not in spec:
            spec["components"] = {}

        # Note: We use a placeholder security scheme. The actual auth is handled
        # by our custom transport layer which adds both headers.
        spec["components"]["securitySchemes"] = {
            "StockTrimAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "api-auth-id",
                "description": "StockTrim authentication (api-auth-id and api-auth-signature)",
            }
        }

        # Add global security requirement
        spec["security"] = [{"StockTrimAuth": []}]

        # Remove api-auth-* parameters from all endpoints
        paths_modified = 0
        params_removed = 0

        for path_item in spec.get("paths", {}).values():
            for method, operation in path_item.items():
                if (
                    method
                    in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "options",
                        "head",
                    ]
                    and "parameters" in operation
                ):
                    original_count = len(operation["parameters"])
                    operation["parameters"] = [
                        p
                        for p in operation["parameters"]
                        if p.get("name") not in ["api-auth-id", "api-auth-signature"]
                    ]
                    removed = original_count - len(operation["parameters"])
                    if removed > 0:
                        params_removed += removed
                        paths_modified += 1

                    # Remove empty parameters list
                    if not operation["parameters"]:
                        del operation["parameters"]

        # Save the fixed spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        logger.info(
            f"✅ Fixed auth in {paths_modified} endpoints ({params_removed} params removed)"
        )
        return True

    except Exception as e:
        logger.error(f"❌ Failed to fix auth in spec: {e}")
        return False


def validate_openapi_spec_python(spec_path: Path) -> bool:
    """Validate the OpenAPI specification using openapi-spec-validator."""
    logger.info("Validating OpenAPI specification with openapi-spec-validator")

    try:
        with open(spec_path) as f:
            spec_dict = yaml.safe_load(f)
        validate_spec(spec_dict)
        logger.info("✅ OpenAPI specification is valid (openapi-spec-validator)")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAPI specification validation failed: {e}")
        return False


def validate_openapi_spec_redocly(spec_path: Path) -> bool:
    """Validate the OpenAPI specification using Redocly CLI."""
    logger.info("Validating OpenAPI specification with Redocly CLI")

    try:
        result = subprocess.run(
            ["npx", "@redocly/cli@latest", "lint", str(spec_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            logger.info("✅ OpenAPI specification is valid (Redocly)")
            return True
        else:
            logger.warning(f"⚠️  Redocly validation warnings:\n{result.stdout}")
            # Don't fail on Redocly warnings, just log them
            return True
    except FileNotFoundError:
        logger.warning("⚠️  Redocly CLI not found (npx not available), skipping")
        return True
    except subprocess.TimeoutExpired:
        logger.warning("⚠️  Redocly validation timed out, skipping")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Redocly validation failed: {e}, skipping")
        return True


def generate_client_to_temp() -> Path:
    """Generate the Python client using openapi-python-client to a temporary directory."""
    logger.info("Generating Python client from OpenAPI spec")

    temp_output = Path(tempfile.mkdtemp(prefix="stocktrim_gen_"))
    logger.info(f"Generating to temporary directory: {temp_output}")

    try:
        cmd = [
            "npx",
            "@hey-api/openapi-ts@latest",
            "--client",
            "axios",
            "--input",
            str(SPEC_FILE),
            "--output",
            str(temp_output),
        ]

        # Use openapi-python-client instead
        cmd = [
            sys.executable,
            "-m",
            "openapi_python_client",
            "generate",
            f"--path={SPEC_FILE}",
            f"--output-path={temp_output}",
            "--meta=none",
            "--overwrite",
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("✅ Generated Python client successfully")

        # Log any warnings or info from the generator
        if result.stdout.strip():
            logger.info(f"Generator output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            logger.warning(f"Generator warnings:\n{result.stderr.strip()}")

        return temp_output

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Client generation failed: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during generation: {e}")
        sys.exit(1)


def _fix_types_imports(target_client_path: Path) -> None:
    """Fix imports from 'types' to 'client_types' in all generated files."""
    logger.info("Fixing imports from 'types' to 'client_types'")

    patterns = [
        (r"from \.\.\.types import", "from ...client_types import"),
        (r"from \.\.types import", "from ..client_types import"),
        (r"from \.types import", "from .client_types import"),
        (
            r"from stocktrim_public_api_client\.types import",
            "from stocktrim_public_api_client.client_types import",
        ),
    ]

    files_changed = 0
    for py_file in target_client_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            original_content = content

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                py_file.write_text(content)
                files_changed += 1
                logger.info(
                    f"   ✅ Fixed imports in {py_file.relative_to(PROJECT_ROOT)}"
                )

        except Exception as e:
            logger.warning(f"⚠️  Failed to fix imports in {py_file}: {e}")

    logger.info(f"✅ Fixed imports in {files_changed} files")


def move_client_to_workspace(workspace_path: Path) -> bool:
    """Move generated client from temp directory to workspace, renaming types.py to client_types.py."""
    logger.info(f"Moving generated client to workspace: {CLIENT_DIR}")

    try:
        # openapi-python-client generates directly to the output path
        # The structure is: output_path/{__init__.py, types.py, models/, api/, client.py, ...}
        generated_client_path = workspace_path

        # Verify this looks like a generated client
        if not (generated_client_path / "__init__.py").exists():
            logger.error(f"❌ No __init__.py found in {generated_client_path}")
            return False

        logger.info(f"Found generated client at: {generated_client_path}")

        # Create target directory structure
        target_client_path = CLIENT_DIR / "generated"
        if target_client_path.exists():
            shutil.rmtree(target_client_path)
        target_client_path.mkdir(parents=True, exist_ok=True)

        # Move files from generated client to target
        # types.py needs to go to package root as client_types.py
        types_moved = False
        for item in generated_client_path.iterdir():
            item_name = item.name

            # Skip metadata files and hidden directories
            if item_name in [
                "pyproject.toml",
                "README.md",
                ".gitignore",
                "poetry.lock",
            ]:
                continue
            if item_name.startswith("."):
                continue

            # Handle types.py rename to client_types.py at package root
            if item_name == "types.py":
                target_item = CLIENT_DIR / "client_types.py"
                shutil.copy2(item, target_item)
                logger.info("   ✅ Moved types.py → client_types.py (package root)")
                types_moved = True
            else:
                # Move everything else to generated subdirectory
                target_item = target_client_path / item_name
                if item.is_dir():
                    shutil.copytree(item, target_item)
                else:
                    shutil.copy2(item, target_item)
                logger.info(f"   ✅ Moved {item_name}")

        if not types_moved:
            logger.warning("⚠️  No types.py file found to rename")

        # Now fix all imports to use client_types
        _fix_types_imports(target_client_path)

        logger.info(f"✅ Successfully moved client to {target_client_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to move client to workspace: {e}")
        return False


def post_process_generated_docstrings(workspace_path: Path) -> bool:
    """Post-process generated docstrings to fix RST formatting issues."""
    logger.info("Post-processing generated docstrings")

    files_changed = 0
    target_client_path = CLIENT_DIR / "generated"

    for py_file in target_client_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            original_content = content

            # Fix common RST issues in docstrings
            # 1. Fix :param: that should be :param name:
            content = re.sub(
                r":param:\s+(\w+)\s+\(([^)]+)\):\s+", r":param \1: (\2) ", content
            )

            # 2. Fix :returns: that should be :return:
            content = content.replace(":returns:", ":return:")

            # 3. Fix missing blank lines before lists in docstrings
            content = re.sub(r'(    """[^\n]+)\n(    - )', r"\1\n\n\2", content)

            if content != original_content:
                py_file.write_text(content)
                files_changed += 1
                logger.info(
                    f"   ✅ Fixed docstrings in {py_file.relative_to(PROJECT_ROOT)}"
                )

        except Exception as e:
            logger.warning(f"⚠️  Failed to fix docstrings in {py_file}: {e}")

    logger.info(f"✅ Fixed docstrings in {files_changed} files")
    return True


def fix_specific_generated_issues(workspace_path: Path) -> bool:
    """Fix specific issues in generated code."""
    logger.info("Fixing specific generated code issues")

    # Fix 1: Modernize Union types to use | syntax in client_types.py (at package root)
    client_types_file = CLIENT_DIR / "client_types.py"
    if client_types_file.exists():
        try:
            content = client_types_file.read_text()
            original_content = content

            # Replace Union[A, B] with A | B
            # Match Union[...] with proper bracket counting
            def replace_union(match: re.Match[str]) -> str:
                union_content = match.group(1)
                # Simple case: Union[A, B] -> A | B
                parts = [p.strip() for p in union_content.split(",")]
                return " | ".join(parts)

            # Handle FileContent specifically
            content = content.replace(
                "FileContent = Union[IO[bytes], bytes, str]",
                "FileContent = IO[bytes] | bytes | str",
            )

            # Handle other simple Union types
            content = re.sub(
                r"Union\[([^\[\]]+)\]",
                lambda m: " | ".join(p.strip() for p in m.group(1).split(",")),
                content,
            )

            if content != original_content:
                client_types_file.write_text(content)
                logger.info("   ✅ Modernized Union types in client_types.py")

        except Exception as e:
            logger.warning(f"⚠️  Failed to fix Union types: {e}")
    else:
        logger.warning(f"⚠️  client_types.py not found at {client_types_file}")

    logger.info("✅ Fixed specific generated code issues")
    return True


def run_ruff_fixes(workspace_path: Path) -> bool:
    """Run ruff auto-fixes on the generated code."""
    logger.info("Running ruff auto-fixes")

    try:
        # Run ruff check with --fix and --unsafe-fixes on the entire package
        cmd = [
            sys.executable,
            "-m",
            "ruff",
            "check",
            str(CLIENT_DIR),
            "--fix",
            "--unsafe-fixes",
        ]

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.stdout.strip():
            logger.info(f"Ruff output:\n{result.stdout.strip()}")

        # Run ruff format on the entire package
        cmd = [
            sys.executable,
            "-m",
            "ruff",
            "format",
            str(CLIENT_DIR),
        ]

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.stdout.strip():
            logger.info(f"Ruff format output:\n{result.stdout.strip()}")

        logger.info("✅ Ruff auto-fixes completed")
        return True

    except Exception as e:
        logger.warning(f"⚠️  Ruff auto-fixes failed: {e}")
        return False


def run_tests(workspace_path: Path) -> bool:
    """Run tests to validate the generated client."""
    logger.info("Running tests to validate generated client")

    try:
        # Use poe test which will run pytest
        cmd = [
            sys.executable,
            "-m",
            "poethepoet",
            "test",
        ]

        # Stream output in real-time
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Print output as it comes
        if process.stdout:
            for line in process.stdout:
                print(line, end="")

        return_code = process.wait()

        if return_code == 0:
            logger.info("✅ Tests passed")
            return True
        else:
            logger.warning(f"⚠️  Tests failed with exit code {return_code}")
            return False

    except Exception as e:
        logger.warning(f"⚠️  Failed to run tests: {e}")
        return False


def main() -> None:
    """Main function to regenerate the StockTrim API client."""
    logger.info("🚀 Starting StockTrim API client regeneration")
    logger.info("")

    # Step 1: Download specification
    logger.info("=" * 60)
    logger.info("STEP 1: Download OpenAPI Specification")
    logger.info("=" * 60)
    spec_content = download_openapi_spec()
    save_spec_file(spec_content)
    logger.info("")

    # Step 2: Fix auth in specification
    logger.info("=" * 60)
    logger.info("STEP 2: Fix Authentication in Specification")
    logger.info("=" * 60)
    if not fix_auth_in_spec(SPEC_FILE):
        logger.error("❌ Failed to fix auth in specification")
        sys.exit(1)
    logger.info("")

    # Step 3: Validate specification
    logger.info("=" * 60)
    logger.info("STEP 3: Validate OpenAPI Specification")
    logger.info("=" * 60)
    python_valid = validate_openapi_spec_python(SPEC_FILE)
    validate_openapi_spec_redocly(SPEC_FILE)  # Redocly validation is optional

    if not python_valid:
        logger.error("❌ OpenAPI specification validation failed")
        sys.exit(1)

    logger.info("")

    # Step 4: Generate client
    logger.info("=" * 60)
    logger.info("STEP 4: Generate Python Client")
    logger.info("=" * 60)
    temp_workspace = generate_client_to_temp()
    logger.info("")

    # Step 5: Move client and rename types.py
    logger.info("=" * 60)
    logger.info("STEP 5: Move Client & Rename types.py → client_types.py")
    logger.info("=" * 60)
    if not move_client_to_workspace(temp_workspace):
        logger.error("❌ Failed to move client to workspace")
        shutil.rmtree(temp_workspace)
        sys.exit(1)
    logger.info("")

    # Step 6: Post-process docstrings
    logger.info("=" * 60)
    logger.info("STEP 6: Post-Process Docstrings")
    logger.info("=" * 60)
    post_process_generated_docstrings(temp_workspace)
    logger.info("")

    # Step 7: Fix specific issues
    logger.info("=" * 60)
    logger.info("STEP 7: Fix Specific Generated Issues")
    logger.info("=" * 60)
    fix_specific_generated_issues(temp_workspace)
    logger.info("")

    # Step 8: Run ruff fixes
    logger.info("=" * 60)
    logger.info("STEP 8: Run Ruff Auto-Fixes")
    logger.info("=" * 60)
    run_ruff_fixes(temp_workspace)
    logger.info("")

    # Step 9: Run tests
    logger.info("=" * 60)
    logger.info("STEP 9: Run Tests")
    logger.info("=" * 60)
    tests_passed = run_tests(temp_workspace)
    logger.info("")

    # Clean up temporary directory
    shutil.rmtree(temp_workspace)
    logger.info("🧹 Cleaned up temporary directory")
    logger.info("")

    # Final summary
    logger.info("=" * 60)
    logger.info("🎉 StockTrim API client regeneration completed!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("✅ Generated client with types.py → client_types.py")
    logger.info("✅ Fixed all imports to use client_types")
    logger.info("✅ Modernized Union types to use | syntax")
    logger.info("✅ Fixed RST docstring formatting")
    logger.info("✅ Ran ruff auto-fixes")

    if tests_passed:
        logger.info("✅ All tests passed")
    else:
        logger.warning("⚠️  Some tests failed - please review")

    logger.info("")
    logger.info("💡 Next steps:")
    logger.info("   1. Review the changes: git diff")
    logger.info("   2. Run manual tests: uv run poe test")
    logger.info("   3. Commit the changes: git add . && git commit")


if __name__ == "__main__":
    main()
