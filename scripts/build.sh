#!/bin/bash
# Build script for aidocs distribution

set -e

echo "🔨 Building aidocs for distribution..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
python3 -m pip install --upgrade build twine

# Run tests
echo "🧪 Running tests..."
python3 -m pytest tests/ -v

# Build package
echo "📦 Building package..."
python3 -m build

# Check package
echo "✅ Checking package..."
python3 -m twine check dist/*

echo "🎉 Build complete! Package ready in dist/"
echo ""
echo "📋 Next steps:"
echo "  • Test install: pip install dist/aidocs-*.whl"
echo "  • Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "  • Upload to PyPI: twine upload dist/*"