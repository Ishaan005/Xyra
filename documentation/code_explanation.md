# Xyra - Code Documentation

This document provides an in-depth explanation of what each block of code in each file does within the Xyra project, a drop-in SaaS infrastructure designed to empower AI-driven companies to monetize flexibly.

## Project Structure Overview

Xyra is structured as a typical FastAPI application with clear separation of concerns:

- `backend/` - Python backend API implementation
  - `main.py` - Application entry point
  - `app/` - Core application code
    - `api/` - API routes and dependencies
    - `core/` - Core functionality and configuration
    - `db/` - Database connection and session management
    - `models/` - SQLAlchemy ORM models
    - `schemas/` - Pydantic schemas for validation and serialization
    - `services/` - Business logic services

## Backend Code Explanation

### main.py

```python
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Business Engine API for AI Agents",
    version="0.1.0",
)
```

This block initializes the FastAPI application with a title, description, and version.

```python
# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This code sets up Cross-Origin Resource Sharing (CORS) middleware to allow web clients from different origins to interact with the API. It reads the allowed origins from the application settings.

```python
# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
```

This line includes the API router with a version prefix (e.g., `/api/v1`), which contains all the endpoint routes.

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

This block runs the application using Uvicorn web server when the script is executed directly. It binds to all network interfaces (0.0.0.0) on port 8000 and enables auto-reload for development.

### app/core/config.py

```python
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Business Engine for AI Agents"
    
    # Secret key for token generation
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Token expiration time in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
```

This section defines the basic application settings, including the API version prefix, project name, JWT secret key generation, and token expiration time.

```python
    # CORS Origins
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
```

This block configures Cross-Origin Resource Sharing (CORS) allowed origins with a validator that handles both string and list inputs, allowing for comma-separated values from environment variables.

```python
    # Database configuration
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "business_engine")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
```

This section configures PostgreSQL database connection settings, reading values from environment variables with fallbacks. It includes a validator that constructs the database URI from individual components.

```python
    # Stripe API key
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    
    # Authentication settings for Azure
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")
    
    # Default admin user
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin")
```

This block configures external service integration settings (Stripe for payments and Azure for security), as well as default superuser credentials for system initialization.

### app/core/security.py

```python
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token settings
ALGORITHM = "HS256"

# Create Azure Key Vault client if configured
key_vault_client = None
if settings.AZURE_KEY_VAULT_URL:
    try:
        # Use DefaultAzureCredential for secure authentication following Azure best practices
        credential = DefaultAzureCredential()
        key_vault_client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    except Exception as e:
        print(f"Failed to initialize Key Vault client: {e}")
```

This section initializes the security components:
- Sets up bcrypt for password hashing
- Defines the JWT algorithm as HS256
- Configures Azure Key Vault integration for secure secret storage if available

```python
def get_secret_key() -> str:
    """
    Get the secret key from Azure Key Vault if configured, otherwise use local setting.
    Following Azure best practices to avoid hardcoded credentials.
    """
    if key_vault_client:
        try:
            return key_vault_client.get_secret("jwt-secret-key").value
        except Exception:
            pass
    return settings.SECRET_KEY
```

This function retrieves the secret key used for JWT token signing, preferring Azure Key Vault if configured, with a fallback to local settings. This follows Azure best practices for secret management.

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)
```

These utility functions handle password verification and hashing using the bcrypt algorithm through Passlib.

```python
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt
```

This function creates a JWT access token with an expiration time, using the subject (typically user ID) and a secure secret key.

### app/db/session.py

```python
# Create SQLAlchemy engine with connection pooling for better performance
# Following Azure best practices for database connection management
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Verify connections before usage to avoid stale connections
    pool_size=10,        # Number of connections to maintain in the pool
    max_overflow=20,     # Max number of connections above pool_size
    pool_timeout=30,     # Seconds to wait before timing out on getting a connection
    pool_recycle=1800,   # Recycle connections after 30 minutes to avoid stale connections
)

# Create session factory with optimized settings
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()
```

This block sets up the SQLAlchemy database engine with optimized connection pooling settings to improve performance and reliability. It creates a session factory for creating database sessions and establishes the base class for all SQLAlchemy models.

```python
# Dependency to get DB session
def get_db():
    """
    Dependency function to get a database session and ensure proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def session_scope():
    """
    Context manager for database sessions with automatic error handling and cleanup.
    Provides automatic rollback on exceptions and automatic closing of the session.
    
    Example usage:
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
```

These functions provide two ways to manage database sessions:
1. `get_db`: A dependency function for FastAPI to inject database sessions into route handlers
2. `session_scope`: A context manager for more explicit session management with automatic commit, rollback, and cleanup

```python
# Add query execution time logging for debugging and performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.5:  # Log slow queries (taking more than 500ms)
        logger.warning(f"Slow query detected: {total:.2f}s - {statement}")
```

These event listeners monitor SQL query execution times and log any queries that take longer than 500ms, which is valuable for performance tuning and identifying bottlenecks.

### app/models/base.py

```python
class BaseModel(Base):
    """
    Base class for all models with common functionality
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @declared_attr
    def __tablename__(cls):
        """
        Generate table name automatically from class name
        """
        return cls.__name__.lower()
```

The BaseModel class is an abstract base class for all SQLAlchemy models. It provides:
- Common fields: primary key ID and timestamp fields for creation and updates
- Automatic table name generation based on the class name
- Timestamp tracking for auditing purposes

### app/models/user.py

```python
class User(BaseModel):
    """
    User model for authentication and organization management
    """
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    
    def __str__(self) -> str:
        return f"User(email={self.email}, organization_id={self.organization_id})"
```

The User model defines the database schema for user accounts with:
- Authentication fields (email and hashed password)
- Profile information (full name)
- Status flags (active status and superuser privileges)
- Organization association through a foreign key
- Relationship to the Organization model for easy navigation
- String representation method for debugging and logging

### app/models/organization.py

```python
class Organization(BaseModel):
    """
    Organization model for grouping users and managing billing settings
    """
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    stripe_customer_id = Column(String, nullable=True, unique=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    billing_models = relationship("BillingModel", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    
    def __str__(self) -> str:
        return f"Organization(name={self.name})"
```

The Organization model represents a tenant in the multi-tenant architecture:
- Basic organization details (name and description)
- Integration with Stripe for payment processing (stripe_customer_id)
- Relationships to related models (users, billing models, agents, invoices)
- String representation method for debugging and logging

### app/models/agent.py

```python
class Agent(BaseModel):
    """
    Agent model for tracking AI agents within an organization
    """
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=True)
    
    # Agent configuration and metadata
    config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # External ID for the agent in the customer's system
    external_id = Column(String, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="agents")
    billing_model = relationship("BillingModel", back_populates="agents")
    activities = relationship("AgentActivity", back_populates="agent")
    costs = relationship("AgentCost", back_populates="agent")
    outcomes = relationship("AgentOutcome", back_populates="agent")
```

The Agent model tracks AI agents that organizations deploy:
- Basic information (name, description)
- Organizational ownership through foreign keys
- Configuration stored as JSON for flexibility
- Status tracking (active status and last active timestamp)
- External ID for integration with customer systems
- Relationships to associated models (organization, billing model, activities, costs, outcomes)

```python
class AgentActivity(BaseModel):
    """
    Tracks agent activities for activity-based billing
    """
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # api_call, query, completion, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)  # Additional information about the activity
    
    # Relationships
    agent = relationship("Agent", back_populates="activities")
```

The AgentActivity model tracks different activities performed by agents:
- Association with an agent through a foreign key
- Type classification of the activity
- Timestamp for when the activity occurred
- Flexible metadata storage as JSON
- Relationship back to the parent agent

```python
class AgentCost(BaseModel):
    """
    Tracks costs associated with agent usage
    """
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    cost_type = Column(String, nullable=False)  # compute, api, labor, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="costs")
```

The AgentCost model records expenses associated with agent operations:
- Association with an agent through a foreign key
- Type classification of the cost
- Amount and currency fields for financial tracking
- Timestamp for when the cost was incurred
- Flexible details storage as JSON
- Relationship back to the parent agent

```python
class AgentOutcome(BaseModel):
    """
    Tracks outcomes generated by agents for outcome-based billing
    """
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    outcome_type = Column(String, nullable=False)  # revenue_uplift, cost_savings, etc.
    value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    verified = Column(Boolean, default=False)  # Whether the outcome has been verified
    
    # Relationships
    agent = relationship("Agent", back_populates="outcomes")
```

The AgentOutcome model captures business value generated by agents:
- Association with an agent through a foreign key
- Type classification of the outcome
- Value and currency fields for financial tracking
- Timestamp for when the outcome was achieved
- Flexible details storage as JSON
- Verification status to confirm the outcome's validity
- Relationship back to the parent agent

### app/models/billing_model.py

```python
class BillingModel(BaseModel):
    """
    BillingModel defines how customers are charged for AI agent usage
    """
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Billing model type: 'seat', 'activity', 'outcome', 'hybrid'
    model_type = Column(String, nullable=False)
    
    # Configuration stored as JSON
    config = Column(JSON, nullable=False, default={})
    
    # Whether this billing model is active
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="billing_models")
    agents = relationship("Agent", back_populates="billing_model")
```

The BillingModel defines pricing strategies for AI agent usage:
- Basic information (name, description)
- Organizational ownership through a foreign key
- Type classification with support for multiple billing approaches
- Configuration stored as JSON for flexibility
- Active status flag
- Relationships to associated models (organization, agents)

```python
class SeatBasedConfig(BaseModel):
    """
    Configuration for seat-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    price_per_seat = Column(Float, nullable=False)
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, quarterly, yearly
    
    # Relationship
    billing_model = relationship("BillingModel", backref="seat_config")
```

The SeatBasedConfig model defines parameters for seat-based pricing:
- Association with a billing model through a foreign key
- Price per seat and billing frequency settings
- Relationship back to the parent billing model

```python
class ActivityBasedConfig(BaseModel):
    """
    Configuration for activity-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    price_per_action = Column(Float, nullable=False)
    action_type = Column(String, nullable=False)  # api_call, query, task, etc.
    
    # Relationship
    billing_model = relationship("BillingModel", backref="activity_config")
```

The ActivityBasedConfig model defines parameters for activity-based pricing:
- Association with a billing model through a foreign key
- Price per action and action type settings
- Relationship back to the parent billing model

```python
class OutcomeBasedConfig(BaseModel):
    """
    Configuration for outcome-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    outcome_type = Column(String, nullable=False)  # revenue_uplift, cost_savings, etc.
    percentage = Column(Float, nullable=False)  # e.g., 5% of revenue uplift
    
    # Relationship
    billing_model = relationship("BillingModel", backref="outcome_config")
```

The OutcomeBasedConfig model defines parameters for outcome-based pricing:
- Association with a billing model through a foreign key
- Outcome type and percentage settings for revenue sharing
- Relationship back to the parent billing model

### app/models/invoice.py

```python
class Invoice(BaseModel):
    """
    Invoice model for tracking billing and payments
    """
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String, nullable=False, unique=True)
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, paid, overdue, cancelled
    
    # Amount information
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Payment details
    payment_method = Column(String, nullable=True)
    stripe_invoice_id = Column(String, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    
    # Additional metadata
    notes = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice")
```

The Invoice model tracks billing and payment information:
- Organizational ownership through a foreign key
- Core invoice details (number, issue date, due date, status)
- Financial information (amounts, currency)
- Payment processing details (method, Stripe integration, payment date)
- Additional metadata for notes and flexible data storage
- Relationships to associated models (organization, line items)

```python
class InvoiceLineItem(BaseModel):
    """
    Line items within an invoice
    """
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    
    # Item details
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Item type and reference
    item_type = Column(String, nullable=False)  # subscription, usage, outcome
    reference_id = Column(Integer, nullable=True)  # ID of the referenced entity (agent, activity, etc.)
    reference_type = Column(String, nullable=True)  # Type of referenced entity (Agent, AgentActivity, etc.)
    
    # Metadata for reporting
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
```

The InvoiceLineItem model represents individual charges within an invoice:
- Association with an invoice through a foreign key
- Item details (description, quantity, pricing)
- Type classification and reference to the source entity
- Flexible metadata storage as JSON
- Relationship back to the parent invoice

## API Endpoints

### app/api/v1/api.py

```python
api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(billing_models.router, prefix="/billing-models", tags=["billing models"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
```

This file defines the main API router and includes all endpoint routers with appropriate URL prefixes and OpenAPI tags for documentation.

### app/api/v1/endpoints/auth.py

```python
@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Authenticate user with email and password
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
```

This endpoint handles user authentication:
- Validates username (email) and password using the login form data
- Checks if the user is active
- Creates and returns a JWT access token with appropriate expiration

```python
@router.get("/me", response_model=schemas.User)
def read_users_me(
    current_user: schemas.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user information
    """
    return current_user
```

This endpoint retrieves the current authenticated user's information based on the JWT token provided in the request.

### app/api/v1/endpoints/users.py

```python
@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    Regular users can only see their own user.
    Superusers can see all users.
    """
    if current_user.is_superuser:
        users = user_service.get_users(db, skip=skip, limit=limit)
    else:
        users = [current_user]
    return users
```

This endpoint retrieves a list of users with role-based access control:
- Superusers can see all users with pagination support
- Regular users can only see their own user information

```python
@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new user.
    Only superusers can create new users.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    user = user_service.create_user(db, user_in=user_in)
    return user
```

This endpoint creates a new user:
- Restricted to superusers only
- Checks for existing users with the same email to avoid duplicates
- Creates and returns the new user

```python
@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    Regular users can only see their own user.
    Superusers can see any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
```

This endpoint retrieves a specific user by ID:
- Checks if the user exists
- Enforces permission checks (users can only access their own records unless they're superusers)
- Returns the requested user if authorized

```python
@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    Regular users can only update their own user.
    Superusers can update any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    return user
```

This endpoint updates a user:
- Checks if the user exists
- Enforces permission checks (users can only update their own records unless they're superusers)
- Updates and returns the user

```python
@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Delete a user.
    Only superusers can delete users.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = user_service.delete_user(db, user_id=user_id)
    return user
```

This endpoint deletes a user:
- Restricted to superusers only
- Checks if the user exists
- Deletes and returns the user information

### app/api/v1/endpoints/organizations.py

The organizations endpoint file implements CRUD operations for organization management with permissions, similar to the users endpoints. It additionally includes:

```python
@router.get("/{organization_id}/stats", response_model=schemas.OrganizationWithStats)
def get_organization_stats(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization statistics including agent counts, costs, and revenues.
    """
    # Permission checks and organization retrieval
    
    # Get organization stats
    stats = organization_service.get_organization_stats(db, org_id=organization_id)
    
    # Combine organization data with stats
    org_dict = organization.__dict__.copy() if hasattr(organization, "__dict__") else {}
    org_data = {
        **org_dict,
        **stats
    }
    
    return org_data
```

This endpoint retrieves detailed statistics for an organization:
- Enforces permission checks based on user roles
- Retrieves organization statistics from the service layer
- Combines the base organization data with statistics for a comprehensive view

### app/api/v1/endpoints/agents.py

The agents endpoint file implements CRUD operations for AI agents with the following notable endpoints:

```python
@router.post("/{agent_id}/activities", response_model=schemas.AgentActivity)
def record_activity(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    activity_in: schemas.AgentActivityCreate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Record activity for an agent.
    
    Users can only record activities for agents in their own organization unless they are superusers.
    """
    # Permission and validation checks
    
    # Record activity
    try:
        activity = agent_service.record_agent_activity(db, activity_in=activity_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return activity
```

This endpoint records agent activities:
- Validates that the agent ID in the path matches the one in the request body
- Enforces permission checks based on organization membership
- Records the activity through the service layer
- Handles validation errors with appropriate HTTP status codes

Similar endpoints exist for recording costs and outcomes, as well as retrieving agent statistics.

## Services

The service layer contains the business logic of the application, separated from the API endpoints. This separation of concerns improves maintainability and testability.

### app/services/user_service.py

This file implements user management functions including:
- User retrieval by various criteria (ID, email)
- Authentication with password verification
- User creation with password hashing
- User updates with special handling for password changes
- User deletion
- User activation/deactivation

### app/services/organization_service.py

This file implements organization management functions including:
- Organization CRUD operations
- Stripe customer creation and management
- Organization statistics collection

### app/services/billing_model_service.py

**Legacy Service (Refactored)**: This file now serves as a thin compatibility layer for existing API endpoints, delegating all business logic to modularized components in the `billing_model/` directory. It maintains backward compatibility while enabling better code organization.

**Key Functions**:
- All CRUD functions now delegate to `app.services.billing_model.crud`
- Maintains identical signatures for backward compatibility
- Provides graceful error handling with optional return types

### app/services/billing_model/ (Modularized Components)

The billing model service has been modularized into focused submodules:

**`crud.py`** - Core CRUD Operations:
- `get_billing_model()` - Retrieve single billing model with eager loading
- `get_billing_models_by_organization()` - List billing models with pagination
- `create_billing_model()` - Create new billing models with validation
- `update_billing_model()` - Update existing billing models
- `delete_billing_model()` - Delete billing models with safety checks

**`validation.py`** - Input Validation & Business Rules:
- `validate_billing_config_from_schema()` - Schema-based validation
- Model-specific validation functions for each billing type
- Comprehensive field validation and business rule enforcement

**`calculation.py`** - Billing Calculations:
- `calculate_cost()` - Main cost calculation logic
- Enhanced outcome-based pricing with multi-tier support
- Risk adjustment, performance bonuses, and volume discounts
- Support for various billing model types

**`config.py`** - Configuration Management:
- Configuration creation helpers for each billing model type
- Configuration cleanup utilities
- Modular approach to managing different config types

**`outcome_tracking.py`** - Outcome Tracking & Verification:
- `record_outcome()` - Record outcome achievements
- `verify_outcome()` - Verify outcome authenticity
- Advanced outcome-based billing calculations
- Outcome metrics and verification rule management

**Benefits of Modularization**:
- Improved maintainability with clear separation of concerns
- Better testability with focused, independent modules
- Enhanced reusability of components across the application
- Easier to extend with new billing model types
- Reduced complexity in individual modules

### app/services/agent_service.py

This file implements agent management functions including:
- Agent CRUD operations
- Activity, cost, and outcome recording
- Agent statistics calculations

### app/services/invoice_service.py

This file implements invoicing functions including:
- Invoice CRUD operations
- Invoice number generation
- Monthly invoice generation based on usage and billing models
- Line item management

## Frontend

The frontend directory appears to be empty or in early development. This would typically contain a web interface for interacting with the API, possibly using a modern JavaScript framework like React, Vue, or Angular.