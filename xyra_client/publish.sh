#!/bin/bash

# Xyra Client SDK - PyPI Publication Script
# This script publishes the package to PyPI with full validation and testing

set -e

echo "🚀 Xyra Client SDK - PyPI Publication"
echo "====================================="

# Change to the xyra_client directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if we're in a git repository
if [ -d ".git" ] || git rev-parse --git-dir > /dev/null 2>&1; then
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --staged --quiet; then
        print_warning "You have uncommitted changes. Consider committing them before publishing."
        read -p "Continue anyway? (y/N): " continue_with_changes
        if [[ $continue_with_changes != "y" && $continue_with_changes != "Y" ]]; then
            print_info "Publication cancelled. Commit your changes and try again."
            exit 0
        fi
    fi
else
    print_warning "Not in a git repository. Version control is recommended for packages."
fi

# Ask user which repository to upload to
echo ""
echo "📦 Select upload target:"
echo "1) TestPyPI (recommended for testing)"
echo "2) PyPI (production)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        REPOSITORY="testpypi"
        REPOSITORY_URL="https://test.pypi.org/simple/"
        print_info "📦 Uploading to TestPyPI..."
        ;;
    2)
        REPOSITORY="pypi"
        REPOSITORY_URL="https://pypi.org/simple/"
        print_warning "📦 Uploading to PyPI (production)..."
        echo ""
        print_warning "⚠️ PRODUCTION UPLOAD WARNING ⚠️"
        echo "You are about to upload to the production PyPI server."
        echo "This cannot be undone. Please ensure:"
        echo "• Version number is correct and unique"
        echo "• Package has been tested on TestPyPI"
        echo "• All documentation is up to date"
        echo "• CHANGELOG.md reflects this version"
        echo ""
        read -p "Are you absolutely sure? Type 'publish-to-production' to confirm: " confirm
        if [[ $confirm != "publish-to-production" ]]; then
            print_info "Upload cancelled. Good choice - test on TestPyPI first!"
            exit 0
        fi
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Run validation first
echo ""
echo "1️⃣ Running comprehensive validation checks..."
if ./validate_package.sh; then
    print_success "All validation checks passed"
else
    print_error "Validation failed. Please fix issues before publishing."
    exit 1
fi

# Clean old builds
echo ""
echo "2️⃣ Cleaning old builds..."
rm -rf build/ dist/ *.egg-info/
print_success "Cleaned build artifacts"

# Build the package
echo ""
echo "3️⃣ Building package..."
if python3 -m build; then
    print_success "Package built successfully"
else
    print_error "Build failed"
    exit 1
fi

# Validate with twine
echo ""
echo "4️⃣ Validating package with twine..."
if python3 -m twine check dist/*; then
    print_success "Package validation passed"
else
    print_error "Package validation failed"
    exit 1
fi

# Show what will be uploaded
echo ""
echo "5️⃣ Package contents:"
ls -la dist/
echo ""

# Final confirmation
if [[ $REPOSITORY == "pypi" ]]; then
    print_warning "⚠️ FINAL WARNING: Publishing to PRODUCTION PyPI"
    read -p "Type 'YES' to proceed: " final_confirm
    if [[ $final_confirm != "YES" ]]; then
        print_info "Upload cancelled."
        exit 0
    fi
fi

# Upload to repository
echo ""
echo "6️⃣ Uploading to $REPOSITORY..."
if python3 -m twine upload --repository $REPOSITORY dist/*; then
    print_success "Upload completed successfully!"
else
    print_error "Upload failed"
    exit 1
fi

# Provide next steps
echo ""
echo "🎉 SUCCESS! Package published to $REPOSITORY"
echo "=============================================="

if [[ $REPOSITORY == "testpypi" ]]; then
    echo ""
    print_info "📋 Next steps for TestPyPI:"
    echo "1. Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xyra-client"
    echo ""
    echo "2. Test functionality:"
    echo "   python3 -c \"from xyra_client import XyraClient; print('✅ Import successful')\""
    echo ""
    echo "3. If all tests pass, publish to production:"
    echo "   ./publish.sh (and choose option 2)"
    echo ""
    echo "4. View on TestPyPI:"
    echo "   https://test.pypi.org/project/xyra-client/"
    
elif [[ $REPOSITORY == "pypi" ]]; then
    echo ""
    print_success "🎊 PRODUCTION RELEASE COMPLETE!"
    echo ""
    print_info "📋 Recommended post-publication steps:"
    echo "1. Test installation from PyPI:"
    echo "   pip install xyra-client"
    echo ""
    echo "2. Create a git tag for this release:"
    echo "   git tag v$(grep '^version' pyproject.toml | cut -d'\"' -f2)"
    echo "   git push origin --tags"
    echo ""
    echo "3. Create a GitHub release"
    echo ""
    echo "4. Update main project documentation"
    echo ""
    echo "5. View on PyPI:"
    echo "   https://pypi.org/project/xyra-client/"
    echo ""
    echo "🎉 Anyone can now install with: pip install xyra-client"
fi

echo ""
print_success "Publication script completed successfully!"

# Build fresh package
echo ""
echo "3. Building fresh package..."
python3 -m build

# Upload package
echo ""
echo "4. Uploading package to $REPOSITORY..."
if [[ $REPOSITORY == "testpypi" ]]; then
    python3 -m twine upload --repository testpypi dist/*
else
    python3 -m twine upload dist/*
fi

echo ""
echo "🎉 Package uploaded successfully!"
echo ""
echo "📋 Installation instructions for users:"
if [[ $REPOSITORY == "testpypi" ]]; then
    echo "   # Install from TestPyPI"
    echo "   pip install --index-url https://test.pypi.org/simple/ xyra-client"
else
    echo "   # Install from PyPI"
    echo "   pip install xyra-client"
fi

echo ""
echo "🔗 Package URLs:"
if [[ $REPOSITORY == "testpypi" ]]; then
    echo "   TestPyPI: https://test.pypi.org/project/xyra-client/"
else
    echo "   PyPI: https://pypi.org/project/xyra-client/"
fi

echo ""
echo "✅ Publication complete!"
