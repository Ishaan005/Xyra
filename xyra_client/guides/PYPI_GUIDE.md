# PyPI Publication Guide for Xyra Client SDK

This guide walks you through publishing the Xyra Client SDK to PyPI so anyone can install it with `pip install xyra-client`.

## Prerequisites

### 1. PyPI Account Setup

1. Create accounts on both:
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. Generate API tokens:
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

3. Configure authentication (choose one method):

   **Option A: Using keyring (recommended)**
   ```bash
   pip install keyring
   python3 -m keyring set https://test.pypi.org/legacy/ __token__
   python3 -m keyring set https://upload.pypi.org/legacy/ __token__
   ```

   **Option B: Using ~/.pypirc file**
   ```bash
   cat > ~/.pypirc << EOF
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
   ```

### 2. Install Build Tools

```bash
pip install --upgrade pip build twine wheel setuptools
```

## Publication Process

### Step 1: Validate the Package

Run the validation script to ensure everything is ready:

```bash
cd /path/to/Xyra/xyra_client
./validate_package.sh
```

This script will:
- Check Python version compatibility
- Verify all required files exist
- Test package imports
- Build the package
- Validate with twine
- Test installation

### Step 2: Test on TestPyPI First

**Always test on TestPyPI before production!**

```bash
# Use the publish script for interactive upload
./publish.sh

# Or manually:
python3 -m build
python3 -m twine upload --repository testpypi dist/*
```

### Step 3: Test Installation from TestPyPI

```bash
# Create a fresh virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ xyra-client

# Test the package
python3 -c "
from xyra_client import XyraClient
print('✓ Package works!')
client = XyraClient('http://localhost:8000', 1, 'test-token')
print('✓ Client instantiation works!')
"

# Clean up
deactivate
rm -rf test_env
```

### Step 4: Publish to Production PyPI

Once TestPyPI works correctly:

```bash
# Use the publish script
./publish.sh

# Or manually:
python3 -m twine upload dist/*
```

### Step 5: Verify Production Installation

```bash
# Create fresh environment
python3 -m venv prod_test
source prod_test/bin/activate

# Install from PyPI
pip install xyra-client

# Test
python3 -c "
from xyra_client import XyraClient
print('✅ Production package works!')
"

# Clean up
deactivate
rm -rf prod_test
```

## Version Management

### Updating the Version

1. Update version in multiple places:
   ```bash
   # xyra_client/__init__.py
   __version__ = "0.1.1"
   
   # setup.py
   version="0.1.1"
   
   # pyproject.toml
   version = "0.1.1"
   ```

2. Update CHANGELOG.md with new features/fixes

3. Commit changes:
   ```bash
   git add .
   git commit -m "Bump version to 0.1.1"
   git tag v0.1.1
   git push origin main --tags
   ```

4. Rebuild and republish:
   ```bash
   rm -rf dist/ build/
   ./validate_package.sh
   ./publish.sh
   ```

## Troubleshooting

### Common Issues

1. **"Package already exists" error**
   - You can't reupload the same version
   - Increment the version number and try again

2. **Authentication errors**
   - Check your API tokens are correct
   - Ensure tokens have upload permissions
   - Try regenerating tokens

3. **Build errors**
   - Run `./validate_package.sh` to diagnose issues
   - Check all required files are present
   - Ensure package structure is correct

4. **Import errors after installation**
   - Check `MANIFEST.in` includes all necessary files
   - Verify `__init__.py` is properly configured
   - Test in clean environment

### Validation Checklist

Before publishing, ensure:
- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] Version number is incremented
- [ ] CHANGELOG.md is updated
- [ ] No sensitive information in code
- [ ] License is appropriate (MIT for open source)
- [ ] URLs in setup.py/pyproject.toml are correct
- [ ] Package builds without errors
- [ ] TestPyPI upload works
- [ ] Installation from TestPyPI works

## Automation

### GitHub Actions (Optional)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        cd xyra_client
        pip install build twine
    - name: Build package
      run: |
        cd xyra_client
        python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        cd xyra_client
        twine upload dist/*
```

## Support

For issues with publication:
1. Check PyPI status page: https://status.python.org/
2. Review PyPI documentation: https://packaging.python.org/
3. Check package on PyPI: https://pypi.org/project/xyra-client/

## Security

- Never commit API tokens to version control
- Use environment variables or keyring for tokens
- Regularly rotate API tokens
- Enable 2FA on PyPI accounts
