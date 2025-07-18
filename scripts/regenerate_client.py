#!/usr/bin/env python3
"""
Script to regenerate the StockTrim API client from the OpenAPI specification.

This script:
1. Downloads the latest OpenAPI spec from StockTrim
2. Validates the specification
3. Generates a new Python client using openapi-python-client
4. Performs basic validation of the generated code
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml
from openapi_spec_validator import validate_spec

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SPEC_URL = "https://api.stocktrim.com/swagger/v1/swagger.json"
SPEC_FILE = PROJECT_ROOT / "stocktrim-openapi.yaml"
GENERATED_DIR = PROJECT_ROOT / "stocktrim_public_api_client" / "generated"


def download_openapi_spec() -> dict[str, Any]:
    """Download the OpenAPI specification from StockTrim."""
    logger.info(f"Downloading OpenAPI spec from {SPEC_URL}")

    try:
        response = httpx.get(SPEC_URL, timeout=30.0)
        response.raise_for_status()
        spec = response.json()
        logger.info("✅ Successfully downloaded OpenAPI specification")
        return spec
    except Exception as e:
        logger.error(f"❌ Failed to download OpenAPI spec: {e}")
        sys.exit(1)


def save_spec_file(spec: dict[str, Any]) -> None:
    """Save the specification as YAML file."""
    logger.info(f"Saving OpenAPI spec to {SPEC_FILE}")

    try:
        with open(SPEC_FILE, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        logger.info("✅ Saved OpenAPI specification")
    except Exception as e:
        logger.error(f"❌ Failed to save spec file: {e}")
        sys.exit(1)


def validate_openapi_spec(spec: dict[str, Any]) -> None:
    """Validate the OpenAPI specification."""
    logger.info("Validating OpenAPI specification")

    try:
        validate_spec(spec)  # type: ignore[arg-type]
        logger.info("✅ OpenAPI specification is valid")
    except Exception as e:
        logger.error(f"❌ OpenAPI specification validation failed: {e}")
        sys.exit(1)


def generate_client() -> None:
    """Generate the Python client using openapi-python-client."""
    import shutil
    import tempfile

    logger.info("Generating Python client from OpenAPI spec")

    # Backup custom files that openapi-python-client might overwrite
    custom_files = ["pyproject.toml", "README.md", ".gitignore"]
    backup_dir = None

    try:
        # Create temporary backup directory
        backup_dir = tempfile.mkdtemp(prefix="stocktrim_backup_")
        logger.info(f"📦 Backing up custom files to {backup_dir}")

        for file in custom_files:
            file_path = PROJECT_ROOT / file
            if file_path.exists():
                backup_path = Path(backup_dir) / file
                shutil.copy2(file_path, backup_path)
                logger.info(f"   ✅ Backed up {file}")

        # Remove existing generated directory
        if GENERATED_DIR.exists():
            shutil.rmtree(GENERATED_DIR)
            logger.info("🗑️  Removed existing generated directory")

        # Generate new client to a temporary location first
        temp_output = tempfile.mkdtemp(prefix="stocktrim_gen_")
        logger.info("Generating to temporary directory...")

        cmd = [
            sys.executable,
            "-m",
            "openapi_python_client",
            "generate",
            f"--path={SPEC_FILE}",
            f"--output-path={temp_output}",
            "--meta=poetry",
            "--overwrite",
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("✅ Generated Python client successfully")

        # Find the generated client directory (openapi-python-client creates based on spec title)
        generated_dirs = [
            d
            for d in Path(temp_output).iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and (d / "__init__.py").exists()
        ]
        if not generated_dirs:
            raise RuntimeError("No generated client directory found")

        generated_client_dir = generated_dirs[0]
        logger.info(f"Found generated client at: {generated_client_dir}")

        # Move only the generated client to our target location
        shutil.move(str(generated_client_dir), str(GENERATED_DIR))
        logger.info(f"✅ Moved generated client to {GENERATED_DIR}")

        # Restore custom files
        logger.info("📦 Restoring custom files...")
        for file in custom_files:
            backup_path = Path(backup_dir) / file
            if backup_path.exists():
                file_path = PROJECT_ROOT / file
                shutil.copy2(backup_path, file_path)
                logger.info(f"   ✅ Restored {file}")

        # Log any warnings or info from the generator
        if result.stdout.strip():
            logger.info(f"Generator output: {result.stdout.strip()}")
        if result.stderr.strip():
            logger.warning(f"Generator warnings: {result.stderr.strip()}")

        # Clean up temporary directory
        shutil.rmtree(temp_output)

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Client generation failed: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during generation: {e}")
        sys.exit(1)
    finally:
        # Clean up backup directory
        if backup_dir and Path(backup_dir).exists():
            shutil.rmtree(backup_dir)
            logger.info("🧹 Cleaned up backup directory")


def main() -> None:
    """Main function to regenerate the StockTrim API client."""
    logger.info("🚀 Starting StockTrim API client regeneration")

    # Step 1: Download specification
    spec = download_openapi_spec()

    # Step 2: Save to file
    save_spec_file(spec)

    # Step 3: Validate specification
    validate_openapi_spec(spec)

    # Step 4: Generate client
    generate_client()

    logger.info("🎉 StockTrim API client regeneration completed successfully!")
    logger.info("💡 Next steps:")
    logger.info("   1. Run 'poetry run poe check' to validate the generated code")
    logger.info("   2. Update any custom wrapper methods if needed")
    logger.info("   3. Run tests to ensure everything works correctly")


if __name__ == "__main__":
    main()
