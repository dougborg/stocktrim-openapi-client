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


def add_nullable_to_date_fields(spec_path: Path) -> bool:
    """Add nullable: true to date/time and scalar fields that can be null.

    The StockTrim API returns null for many date/time and scalar fields,
    but the OpenAPI spec doesn't mark them as nullable. This causes the
    generated Python client to crash when isoparse() tries to parse None values.

    Based on real API evidence documented in docs/contributing/api-feedback.md.
    """
    logger.info("Adding nullable: true to date/time and scalar fields")

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        # Define which fields should be nullable based on real API behavior
        # See docs/contributing/api-feedback.md for evidence
        NULLABLE_FIELDS = {
            "PurchaseOrderResponseDto": [
                "message",  # string
                "orderDate",  # date-time ⚠️ CRITICAL - crashes when null
                "fullyReceivedDate",  # date-time ⚠️ CRITICAL - crashes when null
                "externalId",  # string
                "referenceNumber",  # string
                "location",  # object
            ],
            "PurchaseOrderRequestDto": [
                "orderDate",  # date-time - needs to be nullable to clear dates on update
                "externalId",  # string
                "referenceNumber",  # string
                "location",  # object
            ],
            "PurchaseOrderSupplier": [
                "supplierCode",  # string
            ],
            "PurchaseOrderLineItem": [
                "receivedDate",  # date-time ⚠️ CRITICAL - crashes when null
            ],
        }

        schemas = spec.get("components", {}).get("schemas", {})
        fields_modified = 0
        fields_removed_from_required = 0

        for schema_name, field_names in NULLABLE_FIELDS.items():
            if schema_name not in schemas:
                logger.warning(f"Schema {schema_name} not found in spec")
                continue

            schema = schemas[schema_name]
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            for field_name in field_names:
                if field_name not in properties:
                    logger.warning(f"Field {field_name} not found in {schema_name}")
                    continue

                field = properties[field_name]

                # Add nullable: true if not already present
                if not field.get("nullable", False):
                    # Check if field uses $ref (object reference)
                    # OpenAPI 3.0 ignores nullable: true next to $ref, so use allOf with nullable
                    if "$ref" in field:
                        ref_value = field["$ref"]
                        field.clear()  # Remove $ref and other properties
                        field["allOf"] = [{"$ref": ref_value}]
                        field["nullable"] = True
                        fields_modified += 1
                        logger.info(
                            f"  ✓ Made {schema_name}.{field_name} (object ref) nullable using allOf pattern"
                        )
                    else:
                        # For scalar/date fields, nullable: true works fine
                        field["nullable"] = True
                        fields_modified += 1
                        field_type = field.get("type", "object")
                        field_format = field.get("format", "")
                        type_info = (
                            f"{field_type} ({field_format})"
                            if field_format
                            else field_type
                        )
                        logger.info(
                            f"  ✓ Made {schema_name}.{field_name} ({type_info}) nullable"
                        )

                # Remove from required array if present (nullable fields cannot be required)
                if field_name in required:
                    required.remove(field_name)
                    fields_removed_from_required += 1
                    logger.info(
                        f"  ✓ Removed {schema_name}.{field_name} from required array"
                    )

        # Save the modified spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        logger.info(
            f"✅ Made {fields_modified} fields nullable, "
            f"removed {fields_removed_from_required} from required arrays"
        )
        return True

    except Exception as e:
        logger.error(f"❌ Failed to add nullable to date fields: {e}")
        return False


def add_200_response_to_upsert_endpoints(spec_path: Path) -> bool:
    """Add 200 OK response to POST endpoints that support upsert behavior.

    StockTrim's API uses POST endpoints for both create and update operations.
    When a POST includes a reference identifier (like client_reference_number),
    it updates the existing record and returns 200 OK instead of 201 Created.

    This is non-standard REST behavior but commonly used for upsert operations.
    """
    logger.info("Adding 200 OK response to POST endpoints that support upsert")

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        # Define which POST endpoints support upsert (create OR update)
        # These return 200 when updating, 201 when creating
        UPSERT_ENDPOINTS = [
            "/api/PurchaseOrders",  # Uses client_reference_number as upsert key
            "/api/Products",  # Uses product code as upsert key
        ]

        paths = spec.get("paths", {})
        endpoints_modified = 0

        for endpoint_path in UPSERT_ENDPOINTS:
            if endpoint_path not in paths:
                logger.warning(f"Endpoint {endpoint_path} not found in spec")
                continue

            endpoint = paths[endpoint_path]
            if "post" not in endpoint:
                logger.warning(f"POST method not found for {endpoint_path}")
                continue

            post_operation = endpoint["post"]
            responses = post_operation.get("responses", {})

            # Check if 200 response already exists
            if "200" in responses:
                logger.info(f"  ↷ {endpoint_path} already has 200 response")
                continue

            # Get the 201 response schema to use for 200
            if "201" not in responses:
                logger.warning(f"  ⚠️  {endpoint_path} has no 201 response to copy")
                continue

            # Add 200 response (same schema as 201, but for updates)
            responses["200"] = {
                "description": "Success (Updated)",
                "content": responses["201"]["content"],
            }

            endpoints_modified += 1
            logger.info(f"  ✓ Added 200 OK (update) response to POST {endpoint_path}")

        # Save the modified spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        logger.info(f"✅ Added 200 response to {endpoints_modified} POST endpoints")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to add 200 responses to upsert endpoints: {e}")
        return False


def fix_status_enum_to_integer(spec_path: Path) -> bool:
    """Fix PurchaseOrderStatusDto enum to use integer values.

    The StockTrim API returns integer values (0, 1, 2, 3) for purchase order status,
    but the OpenAPI spec defines it as a string enum ("Draft", "Approved", etc.).
    This causes the generated client to crash when parsing responses.

    This function updates the spec to match the actual API behavior by converting
    the enum to use integer values with x-enum-varnames for human-readable names.
    """
    logger.info("Fixing PurchaseOrderStatusDto enum to use integer values")

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        # Find the status enum
        schemas = spec.get("components", {}).get("schemas", {})
        status_dto = schemas.get("PurchaseOrderStatusDto")

        if not status_dto:
            logger.warning("PurchaseOrderStatusDto not found in spec")
            return False

        # Check if already fixed
        if status_dto.get("type") == "integer":
            logger.info("  ↷ Status enum already uses integer type")
            return True

        # Update to integer enum
        # API returns: 0 = Draft, 1 = Approved, 2 = Sent, 3 = Received
        logger.info("  Converting from string enum to integer enum")
        status_dto["type"] = "integer"
        status_dto["enum"] = [0, 1, 2, 3]
        status_dto["x-enum-varnames"] = ["Draft", "Approved", "Sent", "Received"]
        status_dto["description"] = (
            "Purchase order status (0=Draft, 1=Approved, 2=Sent, 3=Received)"
        )

        # Save the modified spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        logger.info("✅ Fixed status enum to use integer values")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to fix status enum: {e}")
        return False


def fix_delete_responses_to_204(spec_path: Path) -> bool:
    """Update DELETE /api/PurchaseOrders to return 204 No Content.

    The StockTrim API was updated to return 204 No Content for DELETE operations,
    but the OpenAPI spec still documents 200 OK. This updates the spec to match
    the actual API behavior.
    """
    logger.info("Updating DELETE endpoints to return 204 No Content")

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        paths = spec.get("paths", {})
        endpoints_modified = 0

        # UPDATE: Only PurchaseOrders DELETE returns 204
        # Other DELETE endpoints still return 200
        purchase_orders_path = paths.get("/api/PurchaseOrders")
        if purchase_orders_path and "delete" in purchase_orders_path:
            delete_op = purchase_orders_path["delete"]
            responses = delete_op.get("responses", {})

            # Remove 200 response if present
            if "200" in responses:
                del responses["200"]
                logger.info("  ✓ Removed 200 response from DELETE /api/PurchaseOrders")

            # Add 204 response if not present
            if "204" not in responses:
                responses["204"] = {
                    "description": "No Content - Purchase order deleted successfully"
                }
                logger.info("  ✓ Added 204 response to DELETE /api/PurchaseOrders")
                endpoints_modified += 1

        # Save the modified spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        logger.info(f"✅ Updated {endpoints_modified} DELETE endpoints to return 204")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to fix DELETE responses: {e}")
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
    import re

    logger.info("Fixing types imports in generated files...")

    # Find all Python files in the client directory
    updated_files = 0
    for py_file in target_client_path.rglob("*.py"):
        if py_file.name in ["__init__.py", "stocktrim_client.py", "utils.py"]:
            continue  # Skip custom files

        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Replace all patterns of types imports
            # Our structure: stocktrim_public_api_client/generated/api/endpoint/file.py
            # client_types.py is at: stocktrim_public_api_client/client_types.py
            patterns = [
                # API files (4 levels up: endpoint/ -> api/ -> generated/ -> package/)
                (r"from \.\.\.types import", "from ....client_types import"),
                (r"from \.\.\.client_types import", "from ....client_types import"),
                # Model files (3 levels up: models/ -> generated/ -> package/)
                (r"from \.\.types import", "from ...client_types import"),
                (r"from \.\.client_types import", "from ...client_types import"),
                # Direct relative imports (1 dot = same level)
                (r"from \.types import", "from .client_types import"),
                # Absolute imports
                (
                    r"from stocktrim_public_api_client\.generated\.types import",
                    "from stocktrim_public_api_client.client_types import",
                ),
                (
                    r"from stocktrim_public_api_client\.types import",
                    "from stocktrim_public_api_client.client_types import",
                ),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            # Only write if content changed
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                logger.info(
                    f"   ✓ Fixed imports in {py_file.relative_to(target_client_path)}"
                )
                updated_files += 1

        except (UnicodeDecodeError, OSError) as e:
            logger.warning(f"   ⚠️  Skipped {py_file}: {e}")

    logger.info(f"   ✅ Updated imports in {updated_files} files")


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

    # Fix .from_dict() type issues in generated models
    _fix_from_dict_type_issues(workspace_path)

    logger.info("✅ Fixed specific generated code issues")
    return True


def _fix_from_dict_type_issues(workspace_path: Path) -> None:
    """Fix type issues with .from_dict() method calls in generated models."""
    logger.info("Fixing .from_dict() type issues in generated models...")

    models_dir = workspace_path / "stocktrim_public_api_client" / "generated" / "models"
    if not models_dir.exists():
        logger.warning(f"⚠️  Models directory not found: {models_dir}")
        return

    # Files with known .from_dict() type issues based on ty output
    problematic_files = [
        "order_plan_results_dto.py",
        "products_request_dto.py",
        "products_response_dto.py",
        "purchase_order_request_dto.py",
        "purchase_order_response_dto.py",
        "sales_order_with_line_items_request_dto.py",
        "set_inventory_request.py",
        "square_web_hook_object.py",
    ]

    fixed_count = 0
    for filename in problematic_files:
        file_path = models_dir / filename
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text()
            original_content = content

            # Ensure cast and Mapping are imported
            if (
                "from typing import" in content
                and ", cast" not in content
                and "cast," not in content
            ):
                # Add cast to typing imports if not present
                content = re.sub(
                    r"from typing import ([^\n]+)",
                    r"from typing import \1, cast",
                    content,
                )

            if (
                "from collections.abc import" in content
                and ", Mapping" not in content
                and "Mapping," not in content
            ):
                # Add Mapping to collections.abc imports if not present
                content = re.sub(
                    r"from collections\.abc import ([^\n]+)",
                    r"from collections.abc import \1, Mapping",
                    content,
                )

            # Pattern: Add type cast for variables passed to .from_dict()
            # Find: SomeClass.from_dict(variable_name)
            # Replace with: SomeClass.from_dict(cast(Mapping[str, Any], variable_name))
            pattern = r"(\w+)\.from_dict\(\s*(\w+(?:_item)?(?:_data)?)\s*\)"

            def replace_from_dict(match):
                class_name = match.group(1)
                var_name = match.group(2)
                return f"{class_name}.from_dict(cast(Mapping[str, Any], {var_name}))"

            # Apply the fix
            content = re.sub(pattern, replace_from_dict, content)

            if content != original_content:
                file_path.write_text(content)
                logger.info(f"   ✅ Fixed .from_dict() type issues in {filename}")
                fixed_count += 1

        except Exception as e:
            logger.warning(f"⚠️  Failed to fix {filename}: {e}")

    logger.info(
        f"✅ Fixed .from_dict() type issues in {fixed_count} generated model files"
    )


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

    # Step 2.5: Add nullable to date/time fields
    logger.info("=" * 60)
    logger.info("STEP 2.5: Add Nullable to Date/Time Fields")
    logger.info("=" * 60)
    if not add_nullable_to_date_fields(SPEC_FILE):
        logger.error("❌ Failed to add nullable to date/time fields")
        sys.exit(1)
    logger.info("")

    # Step 2.6: Add 200 responses to upsert endpoints
    logger.info("=" * 60)
    logger.info("STEP 2.6: Add 200 OK Responses to Upsert Endpoints")
    logger.info("=" * 60)
    if not add_200_response_to_upsert_endpoints(SPEC_FILE):
        logger.error("❌ Failed to add 200 responses to upsert endpoints")
        sys.exit(1)
    logger.info("")

    # Step 2.7: Fix status enum to use integers
    logger.info("=" * 60)
    logger.info("STEP 2.7: Fix Status Enum to Use Integer Values")
    logger.info("=" * 60)
    if not fix_status_enum_to_integer(SPEC_FILE):
        logger.error("❌ Failed to fix status enum")
        sys.exit(1)
    logger.info("")

    # Step 2.8: Fix DELETE responses to 204
    logger.info("=" * 60)
    logger.info("STEP 2.8: Fix DELETE Responses to 204 No Content")
    logger.info("=" * 60)
    if not fix_delete_responses_to_204(SPEC_FILE):
        logger.error("❌ Failed to fix DELETE responses")
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
    fix_specific_generated_issues(Path.cwd())
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
    logger.info("✅ Made date/time fields nullable (handles null API responses)")
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
