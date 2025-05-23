from fastapi import APIRouter
from app.api.v1.endpoints import agents, billing, invoices, organizations, users, email

api_router = APIRouter()
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
