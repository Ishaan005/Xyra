import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# Import integration layer components for setup
from app.integration.api_gateway import setup_api_gateway

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Business Engine API for AI Agents",
    version="0.1.0",
)

# Setup enhanced API gateway features
app = setup_api_gateway(app)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    print("Starting server Access the API documentation at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)