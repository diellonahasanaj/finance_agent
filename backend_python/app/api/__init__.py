from fastapi import APIRouter
from app.api import auth, finance, analysis, system, testing

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(testing.router, prefix="/testing", tags=["testing"])
