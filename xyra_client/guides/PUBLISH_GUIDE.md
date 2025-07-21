# 🚀 Xyra Client SDK - Publishing to PyPI Guide

This comprehensive guide will help you publish the Xyra Client SDK to PyPI so anyone can install it with `pip install xyra-client`.

## ✅ Pre-Publication Checklist

Before publishing, ensure you have completed all the following:

### 1. Package Validation
```bash
# Run the validation script to ensure everything is ready
./validate_package.sh
```

### 2. Version Management
- [ ] Updated version in `pyproject.toml` 
- [ ] Updated version in `xyra_client/__init__.py`
- [ ] Updated `CHANGELOG.md` with new features/fixes
- [ ] All changes committed to git

### 3. Documentation
- [ ] README.md is comprehensive and up-to-date
- [ ] Examples work correctly
- [ ] API documentation is current

## 🔧 Setup Requirements

### 1. Create PyPI Accounts
1. **TestPyPI Account**: [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. **PyPI Account**: [https://pypi.org/account/register/](https://pypi.org/account/register/)

### 2. Generate API Tokens
1. **TestPyPI Token**: [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
2. **PyPI Token**: [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

### 3. Configure Authentication

**Option A: Using Keyring (Recommended)**
```bash
# Install keyring
pip install keyring

# Store tokens securely
python3 -m keyring set https://test.pypi.org/legacy/ __token__
# Enter your TestPyPI token when prompted

python3 -m keyring set https://upload.pypi.org/legacy/ __token__
# Enter your PyPI token when prompted
```

**Option B: Using ~/.pypirc File**
```bash
# Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
repository = https://test.pypi.org/legacy/
EOF

# Set appropriate permissions
chmod 600 ~/.pypirc
```

## 📦 Publishing Process

### Step 1: Automated Publishing (Recommended)
```bash
# Use the provided script for guided publishing
./publish.sh
```

The script will:
- Run all validation checks
- Build the package
- Allow you to choose TestPyPI or PyPI
- Upload the package
- Provide testing instructions

### Step 2: Manual Publishing

**Clean and Build**
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python3 -m build
```

**Test on TestPyPI First**
```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xyra-client

# Test the installed package
python3 -c "
import xyra_client
print(f'Successfully imported xyra_client version {xyra_client.__version__}')

from xyra_client import XyraClient
client = XyraClient('http://example.com', 1, 'token')
print('XyraClient instantiated successfully')
"
```

**Upload to Production PyPI**
```bash
# Only after successful TestPyPI testing
python3 -m twine upload dist/*
```

**Verify Production Installation**
```bash
# Install from production PyPI
pip install xyra-client

# Test installation
python3 -c "
import xyra_client
from xyra_client import XyraClient
print(f'Production installation successful: {xyra_client.__version__}')
"
```

## 🔄 Version Update Process

When preparing a new release:

### 1. Update Version Numbers
```bash
# Update version in pyproject.toml
# Update version in xyra_client/__init__.py
# Ensure both match exactly
```

### 2. Update Changelog
```bash
# Add new section to CHANGELOG.md
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

### 3. Tag the Release
```bash
# Commit all changes
git add .
git commit -m "Release version X.Y.Z"

# Create and push tag
git tag vX.Y.Z
git push origin main --tags
```

## 🧪 Testing After Publication

### Test Installation in Fresh Environment
```bash
# Create virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install xyra-client

# Test basic functionality
python3 -c "
from xyra_client import XyraClient
client = XyraClient('https://api.xyra.com', 123, 'test-token')
print('✅ Package works correctly')
"

# Cleanup
deactivate
rm -rf test_env
```

### Verify Package Metadata
- Check package page on PyPI: https://pypi.org/project/xyra-client/
- Verify description, links, and classifiers are correct
- Test installation instructions in README

## 🚨 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Check stored tokens
python3 -m keyring get https://upload.pypi.org/legacy/ __token__

# Re-configure if needed
python3 -m keyring set https://upload.pypi.org/legacy/ __token__
```

**Build Errors**
```bash
# Clean everything and rebuild
rm -rf build/ dist/ *.egg-info/
python3 -m build
```

**Package Already Exists**
- You cannot overwrite an existing version on PyPI
- Increment the version number in pyproject.toml and __init__.py
- Rebuild and upload

**Import Errors After Installation**
- Check package structure in dist/ files
- Verify MANIFEST.in includes all necessary files
- Test installation in clean environment

## 📈 Post-Publication

### 1. Update Documentation
- Update main Xyra repository README to mention PyPI installation
- Update project documentation with installation instructions

### 2. Announce Release
- Create GitHub release with changelog
- Update any relevant documentation
- Notify users of the new version

### 3. Monitor
- Watch for issues reported by users
- Monitor download statistics
- Plan next release cycle

## 🔒 Security Considerations

1. **Token Management**
   - Never commit API tokens to git
   - Use keyring or secure .pypirc file
   - Rotate tokens periodically

2. **Package Integrity**
   - Always verify package contents before upload
   - Use `twine check` to validate packages
   - Test installations in clean environments

3. **Version Control**
   - Tag releases in git
   - Maintain clear changelog
   - Never delete published versions

---

For questions or issues, refer to:
- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
