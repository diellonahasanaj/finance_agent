from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.error_handler import add_error_handlers
from app.api import api_router
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title="Personal Finance Advisor Agent", debug=settings.ENV.lower() == "development")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_URLS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Personal Finance Agent API", "status": "running"}
    
    app.include_router(api_router)
    add_error_handlers(app)
    return app
