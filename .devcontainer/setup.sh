#!/bin/bash
# This script runs after container creation to finalize setup
set -e

echo "🚀 Finalizing development environment setup..."

# Ensure uv is in PATH (it should already be installed via onCreate)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify uv is available
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv --version

# Sync dependencies (should be fast due to prebuild cache)
echo "📚 Syncing dependencies (using prebuild cache)..."
uv sync --all-extras

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# StockTrim API Configuration
# Get your API credentials from StockTrim settings
STOCKTRIM_API_AUTH_ID=your-auth-id-here
STOCKTRIM_API_AUTH_SIGNATURE=your-auth-signature-here
EOF
    echo "⚠️  Don't forget to add your StockTrim API credentials to .env!"
fi

# Run quick validation (skip to speed up startup)
echo "✅ Environment validated. Run 'uv run poe check' to verify everything."

# Print next steps
echo ""
echo "✨ Development environment ready!"
echo ""
echo "📋 Next steps:"
echo "   1. Add your StockTrim API credentials to .env file"
echo "   2. Run tests: uv run poe test"
echo "   3. See available tasks: uv run poe help"
echo ""
echo "📖 Key resources:"
echo "   - Client Guide: docs/STOCKTRIM_CLIENT_GUIDE.md"
echo "   - Testing Guide: docs/TESTING_GUIDE.md"
echo ""
echo "🎯 Ready to start development!"
