# Xyra Project Code Explanation

## Document Purpose

This document serves as the primary reference for understanding the Xyra codebase architecture. It is:
- **Living Document**: Continuously updated as the project evolves
- **Reference Resource**: Designed to help new and existing team members understand the code structure
- **Collaborative**: All team members are encouraged to improve and expand this documentation
- **Editable**: This document MUST be maintained and updated to reflect the current state of the codebase

> **Important**: This document is meant for future reference and must be edited as the codebase evolves. Please update relevant sections when making significant changes to the architecture or adding new components.

### How to Maintain This Document

1. When adding new components, create appropriate sections following the existing format
2. When modifying existing functionality, update the corresponding documentation
3. Add code examples where helpful
4. Include rationales for architectural decisions when relevant
5. Update the version history section below when making significant changes

## Version History

| Date | Author | Description of Changes |
|------|--------|------------------------|
| April 11, 2025 | Initial Team | Document creation with basic structure |
| | | |

*Add new rows to this table when making substantial updates to the documentation.*


## Project Overview

Xyra is a platform with a modern backend API built with FastAPI and a frontend (structure not fully detailed). The system handles organizations, users, agents, billing models, invoices, and analytics.

## Root Directory Files

- **LICENSE**: Contains the legal terms for using and distributing this code.
- **README.md**: The welcome document that gives a high-level overview of the project, how to set it up, and how to use it.

## Backend Directory

The backend is a FastAPI-based Python application structured in a modular way.

- **main.py**: The entry point of the backend application. This file initializes the FastAPI app, configures middleware, and imports all the routes.

- **requirements.txt**: Lists all the Python packages needed to run the backend, including:
  - FastAPI framework and Uvicorn server
  - SQLAlchemy for database operations
  - Pydantic for data validation
  - Authentication libraries like python-jose and passlib
  - Stripe for payment processing
  - Azure identity and keyvault for secure credential storage
  - Other utility libraries

### App Directory

This is where most of the backend code lives, organized by functionality.

#### API Module (`app/api/`)

- **deps.py**: Contains dependency injection functions used across different endpoints. These are things like getting the current user, validating tokens, or creating database sessions.

##### V1 API (`app/api/v1/`)

- **api.py**: Acts as a router that collects all endpoint groups and includes them under the `/api/v1` prefix.

###### Endpoints (`app/api/v1/endpoints/`)

- **agents.py**: API endpoints for creating, retrieving, updating, and deleting AI agents.
- **analytics.py**: Endpoints for gathering and presenting usage and performance metrics.
- **auth.py**: Handles user authentication, login, token generation, and password operations.
- **billing_models.py**: Manages different pricing/billing structures for your service.
- **invoices.py**: Endpoints for generating, viewing, and managing customer invoices.
- **organizations.py**: Manages multi-tenant organization data and operations.
- **users.py**: User management endpoints for creating, retrieving, updating user information.

#### Core Module (`app/core/`)

- **config.py**: Manages application configuration using Pydantic's settings management. Loads environment variables and provides typed access to them.
- **security.py**: Houses security-related utilities like password hashing, token generation, and verification.

#### Database Module (`app/db/`)

- **session.py**: Handles database connection setup and session management using SQLAlchemy.

#### Models Module (`app/models/`)

These are the SQLAlchemy ORM models defining your database schema:

- **base.py**: Contains the base model class with common fields and methods.
- **agent.py**: Database model for AI agents and their configurations.
- **billing_model.py**: Defines different pricing tiers and billing structures.
- **invoice.py**: Represents customer invoices and payment records.
- **organization.py**: Multi-tenant organization model.
- **user.py**: User account information including authentication details.

#### Schemas Module (`app/schemas/`)

These are Pydantic models used for data validation and serialization:

- **__init__.py**: Likely imports and exposes key schema classes.
- **agent.py**: Request/response schemas for agent operations.
- **billing_model.py**: Request/response schemas for billing models.
- **invoice.py**: Request/response schemas for invoice operations.
- **organization.py**: Request/response schemas for organization operations.
- **token.py**: JWT token schemas for authentication.
- **user.py**: User data validation schemas.

#### Services Module (`app/services/`)

These files contain the business logic, separated from the API endpoints:

- **agent_service.py**: Business logic for managing agents.
- **billing_model_service.py**: Logic for billing model operations.
- **invoice_service.py**: Handles invoice creation, calculation, and processing.
- **organization_service.py**: Organization management logic.
- **user_service.py**: User management business logic.

## Frontend Directory

The frontend directory is present but its internal structure wasn't fully detailed in the provided workspace structure. This would typically contain a modern JavaScript/TypeScript frontend application built with a framework like React, Vue, or Angular.

## Architecture Patterns

The codebase follows several modern patterns:

1. **Three-tier Architecture**:
   - Presentation layer (API endpoints)
   - Business logic layer (services)
   - Data access layer (models)

2. **Dependency Injection**:
   - Uses FastAPI's dependency system to provide database sessions and user context

3. **Repository Pattern**:
   - Database operations are abstracted within service classes

4. **Schema-based Validation**:
   - Uses Pydantic to validate incoming and outgoing data

This architecture makes the codebase modular, testable, and easier to maintain as it grows.