#!/bin/bash
# Build DEB package locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Building DEB package for Advanced Speedtest CLI"
echo "=============================================="
echo ""

# Check for required tools
if ! command -v debuild &> /dev/null; then
    echo "Error: debuild is not installed"
    echo "Install with: sudo apt install devscripts equivs"
    exit 1
fi

if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Error: dpkg-buildpackage is not installed"
    echo "Install with: sudo apt install build-essential"
    exit 1
fi

echo "Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y \
    debhelper-compat \
    devscripts \
    equivs \
    python3-setuptools \
    python3-all \
    build-essential

echo ""
echo "Installing package dependencies..."
sudo apt-get install -y \
    python3-requests \
    python3-websockets \
    python3-colorama \
    python3-tqdm

echo ""
echo "Building package..."
debuild -us -uc -b

echo ""
echo "Build complete!"
echo "DEB files are available in the parent directory:"
ls -lh ../adv-speedtest-cli*.deb 2>/dev/null || echo "No DEB files found"
echo ""
echo "To install the local package:"
echo "  sudo dpkg -i ../adv-speedtest-cli_*.deb"
echo "  sudo apt-get install -f  # Fix any dependency issues"
