#!/bin/bash
# Pre-Build Validation Checklist
# Run this before attempting to build the DEB package

echo "=========================================="
echo "Pre-Build Validation Checklist"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ERRORS=0
WARNINGS=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file (NOT FOUND)"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    local dir="$1"
    local description="$2"
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description: $dir"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $dir (NOT FOUND)"
        ((ERRORS++))
        return 1
    fi
}

check_executable() {
    local file="$1"
    local description="$2"
    
    if [ -x "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file (executable)"
        return 0
    elif [ -f "$file" ]; then
        echo -e "${YELLOW}⚠${NC} $description: $file (not executable, fixing...)"
        chmod +x "$file"
        ((WARNINGS++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file (NOT FOUND)"
        ((ERRORS++))
        return 1
    fi
}

echo "[1] Python Package Structure"
echo "---"
check_dir "advanced_speedtest_cli" "Python package directory"
check_file "advanced_speedtest_cli/__init__.py" "Package __init__.py"
check_file "advanced_speedtest_cli/__main__.py" "Package __main__.py"
check_file "advanced_speedtest_cli/speedtest.py" "Package speedtest.py"
echo ""

echo "[2] Setup Configuration"
echo "---"
check_file "setup.py" "setup.py configuration"
check_file "readme.md" "README.md"
check_file "requirements.txt" "requirements.txt"
echo ""

echo "[3] Debian Packaging Files"
echo "---"
check_dir "debian" "debian/ directory"
check_file "debian/control" "debian/control"
check_file "debian/changelog" "debian/changelog"
check_executable "debian/rules" "debian/rules"
check_file "debian/copyright" "debian/copyright"
check_file "debian/install" "debian/install"
check_file "debian/postinst" "debian/postinst"
check_file "debian/postrm" "debian/postrm"
check_file "debian/source/format" "debian/source/format"

# Check for problematic files
if [ -f "debian/compat" ]; then
    echo -e "${RED}✗${NC} debian/compat should be removed"
    ((ERRORS++))
else
    echo -e "${GREEN}✓${NC} debian/compat correctly absent"
fi
echo ""

echo "[4] Build Scripts"
echo "---"
check_executable "ppa/build-deb.sh" "ppa/build-deb.sh"
check_executable "ppa/diagnose-build.sh" "ppa/diagnose-build.sh"
check_file "ppa/setup-ppa.sh" "ppa/setup-ppa.sh"
echo ""

echo "[5] CI/CD Configuration"
echo "---"
check_file ".github/workflows/build-deb.yml" "GitHub Actions workflow"
echo ""

echo "[6] Documentation"
echo "---"
check_file "DEB_BUILD_GUIDE.md" "DEB build guide"
check_file "RELEASE_NOTES.md" "Release notes"
echo ""

echo "[7] File Validations"
echo "---"

# Check setup.py content
if grep -q "entry_points" setup.py && grep -q "adv-speedtest-cli=speedtest:main" setup.py; then
    echo -e "${GREEN}✓${NC} setup.py has correct entry point"
else
    echo -e "${RED}✗${NC} setup.py missing or incorrect entry point"
    ((ERRORS++))
fi

# Check debian/control for debhelper-compat
if grep -q "debhelper-compat" debian/control; then
    echo -e "${GREEN}✓${NC} debian/control uses debhelper-compat"
else
    echo -e "${RED}✗${NC} debian/control missing debhelper-compat"
    ((ERRORS++))
fi

# Check if main speedtest.py exists (original)
if [ -f "speedtest.py" ]; then
    echo -e "${GREEN}✓${NC} Original speedtest.py present"
else
    echo -e "${YELLOW}⚠${NC} Original speedtest.py not found (may be in package only)"
fi

echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) fixed${NC}"
    fi
    echo ""
    echo "Ready to build! Run:"
    echo "  bash ppa/build-deb.sh"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    echo ""
    echo "Please fix the errors listed above before building."
    exit 1
fi
