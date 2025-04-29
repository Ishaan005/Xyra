import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from main import app
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User

# Use in-memory SQLite database for tests
default_database_url = "sqlite:///:memory:"
engine = create_engine(
    default_database_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """
    Create database tables and initial superuser before running tests.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    superuser = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    db.add(superuser)
    db.commit()
    db.close()

@pytest.fixture(scope="session")
def db_session():
    """
    Provide a session for tests; data persists across tests.
    """
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture()
def client(db_session):
    """
    Provide a TestClient instance with overridden database dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture()
def token(client):
    """
    Obtain authentication token for the initial superuser.
    """
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "admin@example.com", "password": "adminpass"}
    )
    return response.json()["access_token"]
