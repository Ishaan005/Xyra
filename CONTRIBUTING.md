# Contributing to Xyra

First off, thank you for considering contributing to Xyra! It's people like you that make Xyra such a great tool.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- A virtual environment tool (e.g., venv, virtualenv, or conda)

### Setup

1.  **Fork the Repository**

    Start by forking the main Xyra repository to your GitHub account.

2.  **Clone the Repository**

    Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/YOUR_USERNAME/Xyra.git
    cd Xyra
    ```

3.  **Create a Virtual Environment**

    Navigate to the backend directory and create/activate a virtual environment:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Dependencies**

    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables**

    Create a `.env` file in the `backend` directory:
    ```bash
    cd backend
    cp .env.example .env
    ```
    
    Update the `.env` file with your configuration. Key variables include:

    ```env
    # API Settings
    API_V1_STR=/api/v1
    PROJECT_NAME=Xyra

    # Security
    SECRET_KEY=your-secret-key-for-development
    ACCESS_TOKEN_EXPIRE_MINUTES=11520

    # CORS
    CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080

    # Database
    POSTGRES_SERVER=localhost
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your-postgres-password
    POSTGRES_DB=xyra_db

    # Default Admin User
    FIRST_SUPERUSER=admin@example.com
    FIRST_SUPERUSER_PASSWORD=admin
    ```
    *For `SECRET_KEY`, you can generate one using `python -c 'import secrets; print(secrets.token_hex(32))'`.*

6.  **Database Setup**

    Ensure PostgreSQL is running.
    Create the database (e.g., using `psql`):
    ```sql
    CREATE DATABASE xyra_db;
    ```
    Initialize database models (from the `backend` directory):
    ```bash
    alembic upgrade head
    ```
    Run the initialization script to create the first superuser (from the `backend` directory):
    ```bash
    python init_db.py
    ```

7.  **Running the Backend Application**

    From the `backend` directory:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

8.  **Frontend Setup (if contributing to frontend)**

    Navigate to the `frontend` directory:
    ```bash
    cd ../frontend
    npm install
    npm run dev
    ```
    The frontend will be available at `http://localhost:3000`.


## Style Guides

### Python (Backend)

-   Follow PEP 8 guidelines.
-   Use Black for code formatting.
-   Use Flake8 for linting.
-   Write clear and concise docstrings for all modules, classes, functions, and methods.

### TypeScript/Next.js (Frontend)

-   Follow standard TypeScript and React best practices.
-   Use ESLint and Prettier for code formatting and linting (configurations are in the `frontend` directory).
-   Keep components modular and reusable.

## Pull Request Process

1.  Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2.  Update the `README.md` with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3.  Increase the version numbers in any examples and the `README.md` to the new version that this Pull Request would represent. The versioning scheme we use is SemVer.
4.  You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. See `CODE_OF_CONDUCT.md`.
