"""
Test documentation generation to ensure it works in CI/CD.
"""

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.docs
def test_documentation_builds_successfully():
    """Test that Sphinx documentation builds without errors."""
    if os.getenv("CI_DOCS_BUILD", "false").lower() != "true":
        pytest.skip("Documentation tests only run when CI_DOCS_BUILD=true")

    try:
        # Run the docs build command directly with poethepoet
        result = subprocess.run(
            ["poe", "docs-build"],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for docs build
            cwd=Path(__file__).parent.parent,
        )

        # Check if build succeeded
        assert result.returncode == 0, f"Documentation build failed:\n{result.stderr}"

        # Check that key files were generated
        build_dir = Path(__file__).parent.parent / "docs" / "_build" / "html"
        assert build_dir.exists(), "Documentation build directory not found"

        # Check for main documentation files
        assert (build_dir / "index.html").exists(), "Main index.html not generated"
        assert (
            build_dir / "autoapi" / "stocktrim_public_api_client" / "index.html"
        ).exists(), "API documentation not generated"
        assert (build_dir / "genindex.html").exists(), "General index not generated"

        print("✅ Documentation build successful!")
        print(f"Build output: {build_dir}")

    except subprocess.TimeoutExpired:
        pytest.fail("Documentation build timed out after 5 minutes")
    except Exception as e:
        pytest.fail(f"Documentation build failed with error: {e}")


@pytest.mark.docs
def test_documentation_has_api_reference():
    """Test that API reference documentation is generated."""
    if os.getenv("CI_DOCS_BUILD", "false").lower() != "true":
        pytest.skip("Documentation tests only run when CI_DOCS_BUILD=true")

    build_dir = Path(__file__).parent.parent / "docs" / "_build" / "html"

    # Run docs build first if needed
    if not build_dir.exists():
        subprocess.run(
            ["poe", "docs-build"],
            check=False,
            cwd=Path(__file__).parent.parent,
            timeout=300,  # 5 minutes for docs build
        )

    # Check that API reference exists
    api_dir = build_dir / "autoapi" / "stocktrim_public_api_client"
    assert api_dir.exists(), "API reference directory not found"

    # Check for main classes - adapted for StockTrim structure
    assert (api_dir / "stocktrim_client" / "index.html").exists(), (
        "StockTrimClient documentation not found"
    )

    # Check for generated API modules
    generated_api_dir = api_dir / "generated" / "api"
    if generated_api_dir.exists():
        # Verify some key API modules are documented
        products_api = generated_api_dir / "products" / "index.html"
        customers_api = generated_api_dir / "customers" / "index.html"

        # At least one of these should exist for StockTrim
        has_api_docs = any(
            [
                products_api.exists(),
                customers_api.exists(),
                # Check for any API module
                any((generated_api_dir).glob("*/index.html")),
            ]
        )
        assert has_api_docs, "No generated API documentation found"

    print("✅ API reference documentation generated successfully!")


@pytest.mark.docs
def test_documentation_search_functionality():
    """Test that documentation search index is generated."""
    if os.getenv("CI_DOCS_BUILD", "false").lower() != "true":
        pytest.skip("Documentation tests only run when CI_DOCS_BUILD=true")

    build_dir = Path(__file__).parent.parent / "docs" / "_build" / "html"

    # Run docs build first if needed
    if not build_dir.exists():
        subprocess.run(
            ["poe", "docs-build"],
            check=False,
            cwd=Path(__file__).parent.parent,
            timeout=300,  # 5 minutes for docs build
        )

    # Check that search files exist
    assert (build_dir / "search.html").exists(), "Search page not generated"
    assert (build_dir / "searchindex.js").exists(), "Search index not generated"

    # Check that searchindex.js contains references to our classes
    searchindex_content = (build_dir / "searchindex.js").read_text()
    assert "stocktrimclient" in searchindex_content.lower(), (
        "StockTrimClient not indexed"
    )
    assert "resilientasynctransport" in searchindex_content.lower(), (
        "ResilientAsyncTransport not indexed"
    )

    print("✅ Documentation search functionality working!")


if __name__ == "__main__":
    test_documentation_builds_successfully()
    test_documentation_has_api_reference()
    test_documentation_search_functionality()
    print("\n🎉 All documentation tests passed!")
