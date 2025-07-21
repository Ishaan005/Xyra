#!/bin/bash

# Xyra Client SDK - Pre-publish Validation Script
# This script validates the package before publishing to PyPI

set -e

echo "Xyra Client SDK - Pre-publish Validation"
echo "============================================"

# Change to the xyra_client directory
cd "$(dirname "$0")"

# Check Python version
echo "1. Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "   ✓ Python $PYTHON_VERSION found"
    
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "   ✓ Python version is compatible (>=3.8)"
    else
        echo "   ✗ Python version must be >= 3.8"
        exit 1
    fi
else
    echo "   ✗ Python 3 not found"
    exit 1
fi

# Check required files exist
echo ""
echo "2. Checking required files..."
REQUIRED_FILES=(
    "pyproject.toml" 
    "README.md"
    "LICENSE"
    "MANIFEST.in"
    "requirements.txt"
    "CHANGELOG.md"
    "xyra_client/__init__.py"
    "xyra_client/client.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file is missing"
        exit 1
    fi
done

# Check package structure
echo ""
echo "3. Checking package structure..."
if [[ -d "xyra_client" ]]; then
    echo "   ✓ xyra_client package directory exists"
    if [[ -f "xyra_client/__init__.py" ]]; then
        echo "   ✓ xyra_client/__init__.py exists"
    else
        echo "   ✗ xyra_client/__init__.py missing"
        exit 1
    fi
    if [[ -f "xyra_client/client.py" ]]; then
        echo "   ✓ xyra_client/client.py exists"
    else
        echo "   ✗ xyra_client/client.py missing"
        exit 1
    fi
    if [[ -f "xyra_client/py.typed" ]]; then
        echo "   ✓ xyra_client/py.typed exists (type hints supported)"
    else
        echo "   ! xyra_client/py.typed missing (type hints not advertised)"
    fi
else
    echo "   ✗ xyra_client package directory missing"
    exit 1
fi

# Install build dependencies
echo ""
echo "4. Installing build dependencies..."
pip3 install --upgrade pip build twine wheel setuptools

# Test package import
echo ""
echo "5. Testing package import..."
python3 -c "
try:
    from xyra_client import XyraClient
    import xyra_client
    print('   ✓ Package imports successfully')
    print(f'   ✓ Version: {getattr(xyra_client, \"__version__\", \"unknown\")}')
    
    # Test basic instantiation
    client = XyraClient('http://test.com', 1, 'test-token')
    print('   ✓ XyraClient instantiates successfully')
    
    # Check if client has required methods
    required_methods = ['smart_track', 'record_activity', 'record_cost', 'record_outcome', 'health_check']
    for method in required_methods:
        if hasattr(client, method):
            print(f'   ✓ {method} method available')
        else:
            print(f'   ✗ {method} method missing')
            exit(1)
            
except ImportError as e:
    print(f'   ✗ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'   ✗ Unexpected error: {e}')
    exit(1)
"

# Build the package
echo ""
echo "6. Building the package..."
python3 -m build

# Check built package
echo ""
echo "7. Validating built package..."
if [[ -d "dist" ]]; then
    echo "   ✓ dist directory created"
    
    WHEEL_COUNT=$(ls dist/*.whl 2>/dev/null | wc -l)
    TARBALL_COUNT=$(ls dist/*.tar.gz 2>/dev/null | wc -l)
    
    echo "   ✓ Found $WHEEL_COUNT wheel file(s)"
    echo "   ✓ Found $TARBALL_COUNT source distribution(s)"
    
    if [[ $WHEEL_COUNT -gt 0 && $TARBALL_COUNT -gt 0 ]]; then
        echo "   ✓ Package built successfully"
    else
        echo "   ✗ Package build incomplete"
        exit 1
    fi
else
    echo "   ✗ dist directory not created"
    exit 1
fi

# Check package with twine
echo ""
echo "8. Checking package with twine..."
python3 -m twine check dist/*

# Test install from wheel
echo ""
echo "9. Testing installation from wheel..."
WHEEL_FILE=$(ls dist/*.whl | head -1)
pip3 install --force-reinstall "$WHEEL_FILE"

python3 -c "
from xyra_client import XyraClient
print('   ✓ Package installs and imports from wheel')
"

echo ""
echo "🎉 All validation checks passed!"
echo ""
echo "📦 Package is ready for PyPI publication"
echo ""
echo "🚀 Next steps:"
echo "   1. Test upload to TestPyPI:"
echo "      python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "   2. Test install from TestPyPI:"
echo "      pip install --index-url https://test.pypi.org/simple/ xyra-client"
echo ""
echo "   3. Upload to PyPI:"
echo "      python3 -m twine upload dist/*"
echo ""
echo "Notes:"
echo "   - Make sure you have PyPI account and API tokens set up"
echo "   - Consider using keyring for secure token storage"
echo "   - Test thoroughly on TestPyPI before production upload"
echo ""
echo "PyPI Setup Commands:"
echo "   # Configure PyPI token (recommended)"
echo "   python3 -m keyring set https://upload.pypi.org/legacy/ __token__"
echo ""
echo "   # Or configure in ~/.pypirc"
echo "   [pypi]"
echo "   username = __token__"
echo "   password = pypi-YOUR_API_TOKEN_HERE"
