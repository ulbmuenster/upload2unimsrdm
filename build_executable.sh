#!/bin/bash
# Build standalone executable for the current platform

set -e

echo "Building upload2unimsrdm executable..."

# Install dependencies
echo "Installing dependencies..."
uv sync

# Build executable
echo "Building executable with PyInstaller..."
uv run pyinstaller \
    --onefile \
    --name upload2unimsrdm \
    --clean \
    src/upload2unimsrdm/cli.py

echo ""
echo "Build complete!"
echo "Executable location: dist/upload2unimsrdm"
echo ""
echo "Test it with:"
echo "  ./dist/upload2unimsrdm --help"
