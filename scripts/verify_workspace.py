#!/usr/bin/env python3
"""
Simple verification script to test both API clients can be imported.
This helps verify the VS Code workspace environment setup.
"""

import sys
from pathlib import Path


def test_stocktrim():
    """Test StockTrim client import."""
    try:
        import stocktrim_public_api_client

        print("✅ StockTrim client imported successfully")
        print(f"   Module path: {stocktrim_public_api_client.__file__}")
        return True
    except ImportError as e:
        print(f"❌ StockTrim client import failed: {e}")
        return False


def test_katana():
    """Test Katana client import."""
    try:
        # Add parent directory to find katana client
        katana_path = Path(__file__).parent.parent / "katana-openapi-client"
        if katana_path.exists():
            sys.path.insert(0, str(katana_path))

        import stocktrim_public_api_client

        print("✅ StockTrim client imported successfully")
        print(f"   Module path: {stocktrim_public_api_client.__file__}")
        return True
    except ImportError as e:
        print(f"❌ StockTrim client import failed: {e}")
        return False


def main():
    """Main verification function."""
    print("🔍 Testing API Client Imports")
    print("=" * 40)

    stocktrim_ok = test_stocktrim()
    katana_ok = test_katana()

    print("=" * 40)
    if stocktrim_ok and katana_ok:
        print("🎉 All API clients imported successfully!")
        return 0
    else:
        print("❌ Some imports failed. Check your environment setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
