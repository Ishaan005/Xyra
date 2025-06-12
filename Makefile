# Xyra Development Makefile
# Provides convenient commands for development tasks

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend test test-backend test-frontend lint clean build

# Default target
help: ## Show this help message
	@echo "Xyra Development Commands"
	@echo "========================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation commands
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && python -m pip install --upgrade pip && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# Development commands
dev: ## Start both backend and frontend in development mode
	npm run dev

dev-backend: ## Start only the backend server
	npm run dev:backend

dev-frontend: ## Start only the frontend server
	npm run dev:frontend

# Testing commands
test: ## Run all tests
	npm run test

test-backend: ## Run backend tests
	cd backend && python -m pytest

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# Linting
lint: ## Run linting
	npm run lint

# Build commands
build: ## Build the frontend
	npm run build

# Cleanup commands
clean: ## Clean up build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf .next/ out/ 2>/dev/null || true
