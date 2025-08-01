from fastapi import APIRouter

from app.api.v1.endpoints import (
    users,
    auth,
    organizations,
    billing_models,
    agents,
    analytics,
    invoices,
    integration,
    outcomes,
    api_keys,
)

api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(billing_models.router, prefix="/billing-models", tags=["billing models"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(integration.router, prefix="/integration", tags=["integration"])
api_router.include_router(outcomes.router, tags=["outcomes"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])