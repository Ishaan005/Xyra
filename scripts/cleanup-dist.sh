#!/bin/bash

# Clean up compiled JavaScript files that shouldn't be in source control
echo "Cleaning up dist directories..."

# Remove all dist directories
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove specific problematic files
rm -rf frontend/components/dist/ 2>/dev/null || true
rm -rf frontend/components/ui/dist/ 2>/dev/null || true
rm -rf frontend/components/layout/dist/ 2>/dev/null || true
rm -rf frontend/lib/dist/ 2>/dev/null || true

echo "Cleanup complete!"
