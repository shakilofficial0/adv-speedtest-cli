#!/bin/bash
# DEB Package Build Script
# This script builds the advanced-speedtest-cli DEB package

set -e

echo "===== Advanced Speedtest CLI - DEB Build ====="
echo ""

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "[*] Project Root: $PROJECT_ROOT"
echo "[*] Current Directory: $(pwd)"
echo ""

# Check if required build tools are installed
echo "[*] Checking build dependencies..."
if ! command -v debuild &> /dev/null; then
    echo "[!] debuild not found. Installing build-essential and devscripts..."
    sudo apt-get update
    sudo apt-get install -y build-essential devscripts debhelper dh-python python3-setuptools fakeroot
fi

# Clean previous builds
echo "[*] Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info debian/*.egg-info 2>/dev/null || true
rm -f ../*.deb ../*.dsc ../*.tar.gz ../*.changes ../*.buildinfo 2>/dev/null || true

# Extract version from setup.py
VERSION=$(grep "version=" setup.py | head -1 | sed 's/.*version="\([^"]*\)".*/\1/')
RELEASE="${VERSION}-1"
PACKAGE_NAME="adv-speedtest-cli"

echo "[*] Package: $PACKAGE_NAME"
echo "[*] Version: $VERSION"
echo "[*] Release: $RELEASE"
echo ""

# Build the package
echo "[*] Building DEB package with debuild..."
echo ""
debuild -us -uc -b 2>&1 || {
    echo ""
    echo "===== BUILD FAILED ====="
    echo "[!] debuild failed with exit code $?"
    exit 1
}

echo ""
# Check if build was successful
if [ -f "../${PACKAGE_NAME}_${RELEASE}_all.deb" ]; then
    echo "===== BUILD SUCCESS ====="
    echo "[+] DEB package created: ${PACKAGE_NAME}_${RELEASE}_all.deb"
    DEB_PATH="../${PACKAGE_NAME}_${RELEASE}_all.deb"
    echo "[+] Location: $DEB_PATH"
    echo "[+] Size: $(ls -lh "$DEB_PATH" | awk '{print $5}')"
    echo ""
    echo "To install the package locally:"
    echo "  sudo dpkg -i $DEB_PATH"
    echo "  sudo apt-get install -f  # if there are dependency issues"
    echo ""
else
    echo "===== BUILD FAILED ====="
    echo "[!] DEB package was not created at ../adv-speedtest-cli_${RELEASE}_all.deb"
    exit 1
fi
