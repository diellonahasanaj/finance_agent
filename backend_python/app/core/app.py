from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.error_handler import add_error_handlers
from app.api import api_router

def create_app() -> FastAPI:
    app = FastAPI(title="Personal Finance Advisor Agent", debug=True)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
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
