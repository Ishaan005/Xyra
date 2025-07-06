#!/bin/bash

# Xyra Client SDK Installation Script
# This script helps users install and set up the Xyra Client SDK

set -e

echo "🚀 Xyra Client SDK Installation"
echo "==============================="

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "✓ Python $PYTHON_VERSION found"
    
    # Check if Python version is >= 3.8
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "✓ Python version is compatible (>=3.8)"
    else
        echo "✗ Python version must be >= 3.8"
        exit 1
    fi
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install httpx>=0.23.0

# Install SDK in development mode
echo ""
echo "📦 Installing Xyra Client SDK..."
pip3 install -e .

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python3 -c "
import asyncio
from xyra_client import XyraClient

async def test():
    client = XyraClient('http://localhost:8000', 1, 'test-token')
    print('✓ SDK imports successfully')
    
    methods = ['smart_track', 'health_check', 'get_agent_info']
    for method in methods:
        if hasattr(client, method):
            print(f'✓ {method} method available')
        else:
            print(f'✗ {method} method missing')

asyncio.run(test())
"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📚 Quick Start:"
echo "==============="
echo ""
echo "1. Set up environment variables:"
echo "   export XYRA_BASE_URL='http://localhost:8000'"
echo "   export XYRA_AGENT_ID='1'"
echo "   export XYRA_TOKEN='your-token-here'"
echo ""
echo "2. Test the SDK:"
echo "   python3 -c \"import asyncio; from xyra_client import XyraClient; print('SDK ready!')\""
echo ""
echo "3. Run examples:"
echo "   python3 examples.py"
echo ""
echo "4. Read the documentation:"
echo "   cat README.md"
echo ""
echo "📖 For more information:"
echo "   - README.md - Complete documentation"
echo "   - examples.py - Comprehensive examples"
echo "   - CHANGELOG.md - Release notes"
echo ""
echo "🔧 Need help? Check the health of your setup:"
echo "   python3 -c \"import asyncio; from xyra_client import XyraClient; client = XyraClient('http://localhost:8000', 1, 'your-token'); asyncio.run(client.health_check())\""
