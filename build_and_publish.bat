@echo off
REM Quick reference script for PyPI publication (Windows)

echo ===================================
echo Advanced Speedtest CLI - PyPI Setup
echo ===================================
echo.

REM Check Python version
echo Checking Python version...
python --version
python -c "import sys; assert sys.version_info ^>= (3, 7), 'Python 3.7+ required'"
if errorlevel 1 exit /b 1

REM Install build tools
echo Installing build tools...
pip install --upgrade build twine wheel setuptools
if errorlevel 1 exit /b 1

REM Build distributions
echo Building distributions...
python -m build
if errorlevel 1 exit /b 1

REM Validate distributions
echo Validating distributions...
twine check dist\*
if errorlevel 1 exit /b 1

REM Display next steps
echo.
echo ===================================
echo Build Complete!
echo ===================================
echo.
echo Next steps:
echo 1. Create PyPI account: https://pypi.org/account/register/
echo 2. Generate API token: https://pypi.org/manage/account/tokens/
echo 3. Create %%APPDATA%%\Python\pip\pip.ini with credentials
echo 4. Upload to TestPyPI: twine upload --repository testpypi dist\*
echo 5. Test installation: pip install --index-url https://test.pypi.org/simple/ adv-speedtest-cli
echo 6. Upload to PyPI: twine upload dist\*
echo.
echo Documentation: See PYPI_GUIDE.md
echo.
