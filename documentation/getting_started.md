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

- Python 3.8 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- A virtual environment tool (optional but recommended, e.g., venv, virtualenv, or conda)

## Installation

1. **Clone the Repository**

   Start by cloning the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd Xyra
   ```

2. **Create a Virtual Environment**

   ```bash
   # Using venv
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Configuration

Xyra uses environment variables for configuration. Create a `.env` file in the backend directory with the following settings:

```
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Xyra

# Security
SECRET_KEY=your-secret-key  # Use a secure random string in production
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days

# CORS
CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=xyra_db

# Stripe API (if you're using Stripe for payments)
STRIPE_API_KEY=your-stripe-api-key

# Azure Integration (optional)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_KEY_VAULT_URL=your-key-vault-url

# Default Admin User
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin  # Change this in production
```

Customize these values according to your environment. For production, ensure you use secure passwords and keys.

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

   Create a script to initialize the database models. Save this as `init_db.py` in the backend directory:

   ```python
   from app.db.session import engine
   from app.models.base import Base
   from app.models.user import User
   from app.models.organization import Organization
   from app.models.agent import Agent, AgentActivity, AgentCost, AgentOutcome
   from app.models.billing_model import BillingModel, SeatBasedConfig, ActivityBasedConfig, OutcomeBasedConfig
   from app.models.invoice import Invoice, InvoiceLineItem
   
   # Import all models here to ensure they are registered with the Base metadata
   
   def init_db():
       Base.metadata.create_all(bind=engine)
       print("Database tables created successfully.")
   
   if __name__ == "__main__":
       init_db()
   ```

3. **Run the Initialization Script**

   ```bash
   python init_db.py
   ```

## Running the Application

1. **Start the Development Server**

   ```bash
   # From the backend directory
   python main.py
   ```

   The API will be available at `http://localhost:8000`.

2. **Access the API Documentation**

   The FastAPI automatic documentation is available at:
   
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

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
     -H "Authorization: Bearer YOUR_ACTUAL_TOKEN_HERE"
   ```

## Using the API

Xyra provides several API endpoints to manage organizations, users, agents, billing models, and invoices.

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

1. **Create a Dockerfile**

   Create a `Dockerfile` in the backend directory:

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and Run the Docker Container**

   ```bash
   docker build -t xyra-backend .
   docker run -d -p 8000:8000 --env-file .env --name xyra-backend xyra-backend
   ```

### Azure App Service Deployment

For deploying to Azure App Service, you can:

1. Use the Azure CLI:

   ```bash
   # Login to Azure
   az login

   # Create a resource group
   az group create --name xyra-rg --location eastus

   # Create an App Service Plan
   az appservice plan create --name xyra-plan --resource-group xyra-rg --sku B1 --is-linux

   # Create a Web App
   az webapp create --resource-group xyra-rg --plan xyra-plan --name xyra-backend --runtime "PYTHON|3.9"

   # Configure environment variables
   az webapp config appsettings set --resource-group xyra-rg --name xyra-backend --settings \
     WEBSITES_PORT=8000 \
     SCM_DO_BUILD_DURING_DEPLOYMENT=true \
     API_V1_STR=/api/v1 \
     PROJECT_NAME=Xyra \
     POSTGRES_SERVER=your-postgres-server \
     POSTGRES_USER=your-postgres-user \
     POSTGRES_PASSWORD=your-postgres-password \
     POSTGRES_DB=your-postgres-db

   # Deploy the code
   az webapp deployment source config-local-git --resource-group xyra-rg --name xyra-backend

   # Add a remote to your local git repository
   git remote add azure <git-url-from-previous-command>

   # Push your code
   git push azure main
   ```

2. Create an `azure-pipelines.yml` file for CI/CD with Azure DevOps

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
   # Check PostgreSQL status
   systemctl status postgresql
   
   # Check if you can connect to the database
   psql -U postgres -h localhost -d xyra_db
   ```

2. **JWT Authentication Issues**

   - Ensure your SECRET_KEY is set correctly
   - Check the token expiration time

3. **API Not Starting**

   - Check for errors in the console output
   - Ensure all required environment variables are set
   - Verify that port 8000 is not already in use

   ```bash
   # Check if port 8000 is already in use
   netstat -tuln | grep 8000
   ```

4. **Missing Dependencies**

   - Reinstall dependencies

   ```bash
   pip install -r requirements.txt
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