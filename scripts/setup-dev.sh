#!/bin/bash
# Xyra Development Setup Script
# This script sets up the development environment for Xyra

set -e

echo "🚀 Setting up Xyra development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "README.md" ]; then
    print_error "Please run this script from the Xyra root directory"
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
    print_warning "Python version is $PYTHON_VERSION. Recommended: 3.11 or higher"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_warning "Node.js version is $NODE_VERSION. Recommended: 18 or higher"
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL is not installed or not in PATH. You'll need PostgreSQL 13+ for the backend."
fi

print_status "Prerequisites check completed!"

# Setup backend
print_status "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
print_status "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please update the .env file with your configuration"
    else
        print_error ".env.example not found. Please create a .env file manually."
    fi
else
    print_status ".env file already exists"
fi

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd frontend

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

cd ..

# Final instructions
print_status "Setup completed! "
echo ""
echo "Next steps:"
echo "1. Configure your .env file in the backend directory"
echo "2. Set up PostgreSQL database:"
echo "   - Create database: CREATE DATABASE xyra_db;"
echo "3. Run database migrations:"
echo "   - cd backend && source venv/bin/activate && alembic upgrade head"
echo "4. Initialize the database:"
echo "   - python init_db.py"
echo "5. Start the development servers:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   - Frontend: cd frontend && npm run dev"
echo ""
echo "Or use the convenience commands:"
echo "   - npm run dev (starts both backend and frontend)"
echo "   - npm run install:all (installs all dependencies)"
echo ""
print_status "Happy coding! 🚀"
