import uvicorn
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.api import api_router
from app.core.config import settings
from init_db import init_db

# Import integration layer components for setup
from app.integration.api_gateway import setup_api_gateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrailingSlashMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle trailing slash redirects by removing trailing slashes
    from request paths (except for root "/") to prevent 307 redirects.
    """
    async def dispatch(self, request: Request, call_next):
        url_path = request.url.path
        
        # Remove trailing slash for all paths except root "/"
        if url_path != "/" and url_path.endswith("/"):
            # Create new path without trailing slash
            new_path = url_path.rstrip("/")
            
            # Update the request scope directly
            request.scope["path"] = new_path
            request.scope["raw_path"] = new_path.encode("utf-8")
            
            # Also update the request URL for consistency
            new_url = str(request.url).rstrip("/")
            request.scope["query_string"] = request.url.query.encode("utf-8")
        
        response = await call_next(request)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown events."""
    # Startup: Initialize database automatically
    logger.info("Starting Xyra application...")
    logger.info("Initializing database (if needed)...")
    
    try:
        init_db()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error("Please check your database configuration and try again.")
        raise
    
    logger.info("Xyra application startup completed!")
    yield
    # Shutdown
    logger.info("Shutting down Xyra application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Business Engine API for AI Agents",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# Setup enhanced API gateway features (without health endpoint to avoid conflicts)
# app = setup_api_gateway(app)

# Add trailing slash middleware FIRST (before CORS)
app.add_middleware(TrailingSlashMiddleware)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add comprehensive health check for container monitoring
@app.get("/health")
async def container_health_check():
    """
    Comprehensive health check endpoint for Azure Container Apps
    This endpoint checks database connectivity and overall application health
    """
    from sqlalchemy import text
    from app.db.session import engine
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {
            "database": "unknown",
            "api": "healthy"
        }
    }
    
    # Check database connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

# Add readiness probe endpoint (lighter check for frequent probes)
@app.get("/ready")
async def readiness_check():
    """
    Readiness probe endpoint for Kubernetes-style health checks
    This is a lighter check that can be called frequently
    """
    return {"status": "ready", "timestamp": time.time()}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    print("Starting server Access the API documentation at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)