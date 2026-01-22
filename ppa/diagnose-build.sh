#!/bin/bash
# DEB Build Troubleshooting Script
# Provides detailed debugging information for the build process

set -e

echo "=========================================="
echo "Advanced Speedtest CLI - Build Diagnostics"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "[1] Checking Project Structure"
echo "========================================"
echo "Project Root: $PROJECT_ROOT"
echo ""
echo "Files present:"
ls -la | grep -E "setup.py|readme.md|requirements.txt|debian|advanced_speedtest_cli"
echo ""

echo "[2] Checking Python Setup Configuration"
echo "========================================"
if [ -f setup.py ]; then
    echo "✓ setup.py exists"
    grep -E "name=|version=|packages=" setup.py | head -5
else
    echo "✗ setup.py NOT found"
fi
echo ""

echo "[3] Checking Debian Packaging Files"
echo "========================================"
if [ -d debian ]; then
    echo "✓ debian/ directory exists"
    echo "Contents:"
    ls -la debian/
    echo ""
    
    if [ -f debian/control ]; then
        echo "debian/control content (first 15 lines):"
        head -15 debian/control
        echo ""
    fi
    
    if [ -f debian/rules ]; then
        echo "debian/rules is readable: $(test -x debian/rules && echo 'executable' || echo 'NOT executable')"
        if [ ! -x debian/rules ]; then
            echo "  >> Making debian/rules executable..."
            chmod +x debian/rules
        fi
    fi
    
    if [ -f debian/compat ]; then
        echo "✗ WARNING: debian/compat file still exists!"
        echo "  Content: $(cat debian/compat)"
    else
        echo "✓ debian/compat file correctly removed"
    fi
else
    echo "✗ debian/ directory NOT found"
fi
echo ""

echo "[4] Checking Build Dependencies"
echo "========================================"
echo "Checking for required tools:"
for tool in debuild dpkg-buildpackage dh_python3 python3; do
    if command -v "$tool" &> /dev/null; then
        VERSION=$("$tool" --version 2>&1 | head -1 || echo "N/A")
        echo "✓ $tool: $VERSION"
    else
        echo "✗ $tool: NOT installed"
    fi
done
echo ""

echo "[5] Checking Python Package Structure"
echo "========================================"
if [ -d advanced_speedtest_cli ]; then
    echo "✓ advanced_speedtest_cli/ directory exists"
    ls -la advanced_speedtest_cli/
else
    echo "✗ advanced_speedtest_cli/ directory NOT found"
fi
echo ""

echo "[6] Checking Entry Points"
echo "========================================"
if [ -f advanced_speedtest_cli/__main__.py ]; then
    echo "✓ __main__.py exists"
    head -5 advanced_speedtest_cli/__main__.py
else
    echo "✗ __main__.py NOT found"
fi
echo ""

echo "[7] Build Environment Summary"
echo "========================================"
echo "Current User: $(whoami)"
echo "Current Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "Python Location: $(which python3)"
echo ""

echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review any ✗ warnings above"
echo "2. Fix missing files or incorrect permissions"
echo "3. Run: bash ppa/build-deb.sh"
echo ""
