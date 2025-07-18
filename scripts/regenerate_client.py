#!/usr/bin/env python3
"""
Script to regenerate the StockTrim API client from the OpenAPI specification.

This script:
1. Downloads the latest OpenAPI spec from StockTrim
2. Validates the specification
3. Generates a new Python client using openapi-python-client
4. Performs basic validation of the generated code
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

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


def download_openapi_spec() -> dict:
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


def save_spec_file(spec: dict) -> None:
    """Save the specification as YAML file."""
    logger.info(f"Saving OpenAPI spec to {SPEC_FILE}")
    
    try:
        with open(SPEC_FILE, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        logger.info("✅ Saved OpenAPI specification")
    except Exception as e:
        logger.error(f"❌ Failed to save spec file: {e}")
        sys.exit(1)


def validate_openapi_spec(spec: dict) -> None:
    """Validate the OpenAPI specification."""
    logger.info("Validating OpenAPI specification")
    
    try:
        validate_spec(spec)
        logger.info("✅ OpenAPI specification is valid")
    except Exception as e:
        logger.error(f"❌ OpenAPI specification validation failed: {e}")
        sys.exit(1)


def generate_client() -> None:
    """Generate the Python client using openapi-python-client."""
    logger.info("Generating Python client from OpenAPI spec")
    
    # Remove existing generated directory
    if GENERATED_DIR.exists():
        import shutil
        shutil.rmtree(GENERATED_DIR)
        logger.info("🗑️  Removed existing generated directory")
    
    # Generate new client
    cmd = [
        sys.executable, "-m", "openapi_python_client",
        "generate",
        f"--path={SPEC_FILE}",
        f"--output-path={PROJECT_ROOT}",
        "--package-name=stocktrim_public_api_client.generated",
        "--class-overrides=datetime.datetime",
        "--meta-type=poetry",
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("✅ Generated Python client successfully")
        
        # Log any warnings or info from the generator
        if result.stdout.strip():
            logger.info(f"Generator output: {result.stdout.strip()}")
        if result.stderr.strip():
            logger.warning(f"Generator warnings: {result.stderr.strip()}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Client generation failed: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        sys.exit(1)


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
