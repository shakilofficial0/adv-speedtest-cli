#!/bin/bash
# Quick reference script for PyPI publication

echo "==================================="
echo "Advanced Speedtest CLI - PyPI Setup"
echo "==================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python --version
python -c "import sys; assert sys.version_info >= (3, 7), 'Python 3.7+ required'"

# Check required tools
echo "✓ Checking required tools..."
command -v pip &> /dev/null || { echo "pip not found"; exit 1; }

# Install build tools
echo "✓ Installing build tools..."
pip install --upgrade build twine wheel setuptools

# Build distributions
echo "✓ Building distributions..."
python -m build

# Validate distributions
echo "✓ Validating distributions..."
twine check dist/*

# Display next steps
echo ""
echo "==================================="
echo "Build Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Create PyPI account: https://pypi.org/account/register/"
echo "2. Generate API token: https://pypi.org/manage/account/tokens/"
echo "3. Create ~/.pypirc with credentials"
echo "4. Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "5. Test installation: pip install --index-url https://test.pypi.org/simple/ adv-speedtest-cli"
echo "6. Upload to PyPI: twine upload dist/*"
echo ""
echo "Documentation: See PYPI_GUIDE.md"
