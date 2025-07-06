# Getting Started with Xyra Backend

This guide provides step-by-step instructions on how to set up, configure, and run the Xyra backend system - a drop-in SaaS infrastructure designed to empower AI-driven companies to monetize flexibly.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Authentication](#authentication)
7. [Using the API](#using-the-api)
8. [Deployment Options](#deployment-options)
9. [Azure Integration](#azure-integration)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11 or higher (recommended for optimal performance)
- Node.js 18 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- npm (Node.js package manager)
- A virtual environment tool (optional but recommended, e.g., venv, virtualenv, or conda)

## Installation

### Option A: Automated Setup (Recommended)

1. **Clone the Repository**

   Start by cloning the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd Xyra
   ```

2. **Run the Setup Script**

   For a quick and automated setup, use the provided setup script:

   ```bash
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

   This script will:
   - Check all prerequisites
   - Set up Python virtual environment
   - Install backend dependencies
   - Install frontend dependencies
   - Create `.env` file from template
   - Provide next steps instructions

### Option B: Manual Setup

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd Xyra
   ```

2. **Install All Dependencies Using npm**

   From the project root:

   ```bash
   npm run install:all
   ```

   This command will install both backend and frontend dependencies automatically.

3. **Manual Installation (Alternative)**

   If you prefer to install dependencies step by step:

   ```bash
   # Backend dependencies
   cd backend
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   cd ..
   
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

### Option C: Using Make Commands

If you prefer using Make commands:

```bash
# Show all available commands
make help

# Install all dependencies
make install

# Install only backend dependencies
make install-backend

# Install only frontend dependencies
make install-frontend
```

## Configuration

Xyra uses environment variables for configuration. The easiest way to set up your configuration is to use the provided template:

### Backend Configuration

1. **Copy the Environment Template**

   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit the Configuration**

   Open the `.env` file and customize the values according to your environment:

```bash
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Xyra

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS
CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=xyra_db

# Default Admin User (for development)
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme

# Optional: Azure Integration
# AZURE_CLIENT_ID=your-azure-client-id
# AZURE_CLIENT_SECRET=your-azure-client-secret
# AZURE_TENANT_ID=your-azure-tenant-id

# Optional: Stripe Integration
# STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
# STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key

# Optional: Redis Configuration (for caching)
# REDIS_URL=redis://localhost:6379/0

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

**Important Security Notes:**
- Generate a secure SECRET_KEY for production: `openssl rand -hex 32`
- Change the default FIRST_SUPERUSER_PASSWORD
- Use secure passwords and keys for all services

### Frontend Configuration

The frontend automatically uses the backend API configuration. If you need custom frontend environment variables, create a `.env.local` file in the `frontend` directory.

## Database Setup

1. **Create a PostgreSQL Database**

   ```bash
   # Access PostgreSQL
   psql -U postgres
   
   # Create the database
   CREATE DATABASE xyra_db;
   
   # Exit PostgreSQL
   \q
   ```

2. **Initialize Database Models**

   The Xyra project includes an `init_db.py` script that handles database initialization. This script:
   - Creates all database tables
   - Sets up proper Azure PostgreSQL connection handling
   - Creates the initial superuser if specified in environment variables
   - Includes retry logic and proper error handling

3. **Run Database Migrations (Recommended)**

   For production environments, use Alembic migrations instead of the init script:

   ```bash
   cd backend
   # Apply all migrations
   alembic upgrade head
   ```

   The project includes comprehensive migration files that handle schema changes and data updates.

4. **Alternative: Run the Initialization Script**

   For development or initial setup:

   ```bash
   cd backend
   python init_db.py
   ```

## Running the Application

Xyra provides multiple convenient ways to run the application:

### Option A: Using npm Scripts (Recommended)

   From the project root directory:
   ```bash
   # Start both backend and frontend simultaneously
   npm run dev
   
   # Or start them separately
   npm run dev:backend  # Backend only (port 8000)
   npm run dev:frontend # Frontend only (port 3000)
   
   # For production builds
   npm run build        # Build frontend
   npm run start        # Start both in production mode
   ```

### Option B: Using Make Commands

   ```bash
   # Start development servers (both backend and frontend)
   make dev
   
   # Start only backend
   make dev-backend
   
   # Start only frontend  
   make dev-frontend
   
   # Build the application
   make build
   ```

### Option C: Manual Startup

   **Backend:**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   **Frontend (in another terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

### Access Points

- **API Backend**: `http://localhost:8000`
- **Frontend Application**: `http://localhost:3000`
- **API Documentation**: 
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

## Testing

Xyra includes comprehensive test suites for both backend and frontend:

### Running Tests

```bash
# Run all tests
npm run test

# Run backend tests only
npm run test
# or
make test-backend
cd backend && python -m pytest

# Run frontend tests only
npm run test:frontend
# or
make test-frontend

# Run linting
npm run lint
# or
make lint
```

### Test Coverage

The backend tests cover:
- API endpoints and authentication
- Database models and operations
- Business logic and validations
- Integration with external services

The frontend tests include:
- Component functionality
- User interactions
- API integration
- UI/UX behavior

## Authentication

Xyra uses JWT (JSON Web Tokens) for authentication.

1. **Create a Superuser**

   The application will automatically create a superuser during startup if one doesn't exist, using the `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD` environment variables.

2. **Get an Access Token**

   To authenticate, send a POST request to `/api/v1/auth/login/access-token` with your email and password:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=admin"
   ```

   This will return a JSON response with an access token:

   ```json
   {
     "access_token": "<insert-token-here>",
     "token_type": "bearer"
   }
   ```

3. **Use the Token in API Requests**

   Include the token in the Authorization header of your requests:

   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <YOUR_ACTUAL_TOKEN_HERE>"
   ```

## Using the API

Xyra provides several ways to interact with the API:

### Python SDK (xyra_client)

For Python applications, use the official Xyra Python SDK:

```bash
# Install the Xyra client SDK
cd xyra_client
pip install -e .
```

Example usage:
```python
import asyncio
from xyra_client import XyraClient

async def main():
    # Initialize the client
    client = XyraClient(
        base_url="http://localhost:8000",
        agent_id=1,  # Your agent ID
        token="your-api-token"  # Your API token
    )
    
    # Check health
    health = await client.health_check()
    print(f"Status: {health['status']}")
    
    # Smart tracking - works with any billing model
    result = await client.smart_track(
        value=100.0,  # For outcome-based models
        activity_units=1,  # For activity-based models
        workflow_type="default",  # For workflow-based models
        metadata={"user_id": "demo_user"}
    )
    
    print(f"Tracking result: {result}")
    
    # Get billing summary
    summary = await client.get_billing_summary()
    print(f"Billing summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Key SDK Features:

- **Smart Tracking**: Automatically adapts to your billing model
- **All Billing Models**: Agent, Activity, Outcome, Workflow, and Hybrid
- **Health Checks**: Validate configuration and connectivity
- **Analytics**: Get billing summaries, stats, and cost estimates
- **Error Handling**: Comprehensive error handling and validation
- **Type Safety**: Full type hints for better IDE support

#### SDK Methods:

```python
# Smart tracking (recommended)
await client.smart_track(value=100.0, metadata={"user": "demo"})

# Specific recording
await client.record_activity("data_processing", {"records": 1000})
await client.record_cost(10.50, "compute", "USD")
await client.record_outcome("sale", 500.0, "USD", {"deal_id": "D123"})
await client.record_workflow("lead_research", {"industry": "tech"})

# Information and analytics
agent_info = await client.get_agent_info()
billing_config = await client.get_billing_config()
stats = await client.get_agent_stats()
summary = await client.get_billing_summary()

# Utilities
health = await client.health_check()
estimate = await client.estimate_cost(activity_units=10)
```

See `xyra_client/README.md` and `xyra_client/examples.py` for comprehensive documentation and examples.

### Direct API Access

You can also interact directly with the REST API using curl, Postman, or any HTTP client.

### Key Endpoints

- **Authentication**: `/api/v1/auth/*`
  - Login: `POST /api/v1/auth/login/access-token`
  - Current user: `GET /api/v1/auth/me`

- **Users**: `/api/v1/users/*`
  - List users: `GET /api/v1/users/`
  - Create user: `POST /api/v1/users/`
  - Get user: `GET /api/v1/users/{user_id}`
  - Update user: `PUT /api/v1/users/{user_id}`
  - Delete user: `DELETE /api/v1/users/{user_id}`

- **Organizations**: `/api/v1/organizations/*`
  - List organizations: `GET /api/v1/organizations/`
  - Create organization: `POST /api/v1/organizations/`
  - Get organization: `GET /api/v1/organizations/{organization_id}`
  - Update organization: `PUT /api/v1/organizations/{organization_id}`
  - Delete organization: `DELETE /api/v1/organizations/{organization_id}`
  - Get organization stats: `GET /api/v1/organizations/{organization_id}/stats`

- **Agents**: `/api/v1/agents/*`
  - List agents: `GET /api/v1/agents/?org_id={organization_id}`
  - Create agent: `POST /api/v1/agents/`
  - Get agent: `GET /api/v1/agents/{agent_id}`
  - Update agent: `PUT /api/v1/agents/{agent_id}`
  - Delete agent: `DELETE /api/v1/agents/{agent_id}`
  - Record activity: `POST /api/v1/agents/{agent_id}/activities`
  - Record cost: `POST /api/v1/agents/{agent_id}/costs`
  - Record outcome: `POST /api/v1/agents/{agent_id}/outcomes`
  - Get agent stats: `GET /api/v1/agents/{agent_id}/stats`

- **Billing Models**: `/api/v1/billing-models/*`
  - List billing models: `GET /api/v1/billing-models/?org_id={organization_id}`
  - Create billing model: `POST /api/v1/billing-models/`
  - Get billing model: `GET /api/v1/billing-models/{model_id}`
  - Update billing model: `PUT /api/v1/billing-models/{model_id}`
  - Delete billing model: `DELETE /api/v1/billing-models/{model_id}`
  - Calculate cost: `POST /api/v1/billing-models/{model_id}/calculate`

- **Invoices**: `/api/v1/invoices/*`
  - List invoices: `GET /api/v1/invoices/?org_id={organization_id}`
  - Create invoice: `POST /api/v1/invoices/`
  - Get invoice: `GET /api/v1/invoices/{invoice_id}`
  - Update invoice: `PUT /api/v1/invoices/{invoice_id}`
  - Cancel invoice: `POST /api/v1/invoices/{invoice_id}/cancel`
  - Mark invoice as paid: `POST /api/v1/invoices/{invoice_id}/pay`
  - Generate monthly invoice: `POST /api/v1/invoices/generate/monthly`

- **Analytics**: `/api/v1/analytics/*`
  - Get organization summary: `GET /api/v1/analytics/organization/{org_id}/summary`
  - Get top agents: `GET /api/v1/analytics/organization/{org_id}/top-agents`
  - Get activity breakdown: `GET /api/v1/analytics/organization/{org_id}/activity-breakdown`

- **Integration**: `/api/v1/integration/*`
  - Webhook management and processing
  - Data connectors and external system integration
  - Batch data import/export functionality
  - Real-time streaming integration

### Example Workflow

Here's a common workflow for setting up a new organization with agents and billing:

1. Authenticate and get a token
2. Create a new organization
3. Create users for the organization
4. Create billing models for the organization
5. Create agents for the organization
6. Record agent activities, costs, and outcomes
7. Generate invoices based on the billing model

## Deployment Options

### Docker Deployment

1. **Using the Production Multi-Stage Dockerfile**

   Xyra includes a production-ready multi-stage Dockerfile that builds both frontend and backend:

   ```bash
   # Build the Docker image (from project root)
   docker build -t xyra .
   
   # Run the container with environment file
   docker run -d -p 3000:3000 --env-file backend/.env --name xyra-app xyra
   ```

   The container runs both the Next.js frontend (port 3000) and FastAPI backend (port 8000) using supervisord for process management.

2. **Using Docker Compose (Development)**

   For development with external services, use the included docker-compose.yml:

   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop services
   docker-compose down
   ```

3. **Environment Variables for Docker**

   Make sure your backend `.env` file is properly configured before running Docker containers. The Docker setup will automatically use the environment variables from your `.env` file.

## Azure Integration

Xyra integrates with Azure services for enhanced security and scalability:

### Azure Key Vault for Secret Management

1. **Create a Key Vault**

   ```bash
   az keyvault create --name xyra-keyvault --resource-group xyra-rg --location eastus
   ```

2. **Add Secrets to Key Vault**

   ```bash
   az keyvault secret set --vault-name xyra-keyvault --name "jwt-secret-key" --value "your-secret-key"
   az keyvault secret set --vault-name xyra-keyvault --name "postgres-password" --value "your-postgres-password"
   ```

3. **Configure Xyra to Use Key Vault**

   Set the following environment variables:

   ```
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_KEY_VAULT_URL=https://xyra-keyvault.vault.azure.net/
   ```

### Azure Database for PostgreSQL

1. **Create a PostgreSQL Server**

   ```bash
   az postgres server create \
     --resource-group xyra-rg \
     --name xyra-postgres \
     --location eastus \
     --admin-user postgres \
     --admin-password your-secure-password \
     --sku-name GP_Gen5_2
   ```

2. **Configure Firewall Rules**

   ```bash
   # Allow Azure services
   az postgres server firewall-rule create \
     --resource-group xyra-rg \
     --server-name xyra-postgres \
     --name AllowAllAzureIPs \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

3. **Create a Database**

   ```bash
   az postgres db create \
     --resource-group xyra-rg \
     --server-name xyra-postgres \
     --name xyra_db
   ```

4. **Update Xyra Configuration**

   Update your `.env` file or environment variables:

   ```
   POSTGRES_SERVER=xyra-postgres.postgres.database.azure.com
   POSTGRES_USER=postgres@xyra-postgres
   POSTGRES_PASSWORD=your-secure-password
   POSTGRES_DB=xyra_db
   ```

## Troubleshooting

### Common Issues and Solutions

1. **Database Connection Issues**

   - Check that PostgreSQL is running
   - Verify the database credentials in your `.env` file
   - Make sure the database has been created

   ```bash
   # Check PostgreSQL status (Linux/macOS)
   brew services list | grep postgresql  # macOS with Homebrew
   systemctl status postgresql           # Linux
   
   # Check if you can connect to the database
   psql -U postgres -h localhost -d xyra_db
   ```

2. **JWT Authentication Issues**

   - Ensure your SECRET_KEY is set correctly and is sufficiently secure
   - Check the token expiration time
   - Regenerate the secret key: `openssl rand -hex 32`

3. **API Not Starting**

   - Check for errors in the console output
   - Ensure all required environment variables are set
   - Verify that port 8000 is not already in use

   ```bash
   # Check if port 8000 is already in use
   netstat -tuln | grep 8000      # Linux
   lsof -i :8000                  # macOS
   ```

4. **Missing Dependencies**

   - Reinstall dependencies

   ```bash
   # Backend dependencies
   cd backend && pip install -r requirements.txt
   
   # Frontend dependencies  
   cd frontend && npm install
   
   # Or use convenience commands
   npm run install:all
   make install
   ```

5. **Build Issues**

   - Clean build artifacts and caches

   ```bash
   # Using Make
   make clean
   
   # Manual cleanup
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
   find . -type f -name "*.pyc" -delete 2>/dev/null || true
   cd frontend && rm -rf .next/ out/ 2>/dev/null || true
   ```

6. **Permission Issues (macOS/Linux)**

   - Make sure the setup script is executable:
   
   ```bash
   chmod +x scripts/setup-dev.sh
   ```

### Logging

Xyra includes comprehensive logging:

1. **Access Logs**

   API request logs are output to the console by default.

2. **Database Query Logs**

   Slow queries (taking more than 500ms) are logged with a warning.

3. **Application Logs**

   Application-specific logs are emitted by the service layers.

4. **Azure Application Insights Integration**

   For production deployments, you can add Azure Application Insights for monitoring and diagnostics:

   ```python
   # Add to requirements.txt
   opencensus-ext-azure==1.1.7
   
   # Add to main.py
   from opencensus.ext.azure.log_exporter import AzureLogHandler
   
   logging.getLogger().addHandler(AzureLogHandler(
       connection_string='InstrumentationKey=your-instrumentation-key')
   )
   ```

For more information about Xyra's API and features, please refer to the [code documentation](./code_explanation.md) in this repository.

## Quick Reference

### Development Commands

```bash
# Setup and Installation
./scripts/setup-dev.sh         # Automated setup
npm run install:all            # Install all dependencies
make install                   # Install using Make

# Development
npm run dev                    # Start both backend and frontend  
npm run dev:backend           # Start backend only
npm run dev:frontend          # Start frontend only
make dev                      # Start development servers

# Testing
npm run test                  # Run all tests
npm run test:frontend         # Run frontend tests
make test-backend             # Run backend tests
npm run lint                  # Run linting

# Building and Deployment
npm run build                 # Build frontend
docker build -t xyra .        # Build Docker image
docker-compose up -d          # Start with Docker Compose

# Maintenance
make clean                    # Clean build artifacts
make help                     # Show all Make commands
```

### Important URLs

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8000  
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Configuration Files

- **Backend Environment**: `backend/.env` (copy from `backend/.env.example`)
- **Frontend Environment**: `frontend/.env.local` (optional)
- **Docker Compose**: `docker-compose.yml`
- **Database Migrations**: `backend/alembic/`