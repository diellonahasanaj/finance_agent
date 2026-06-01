from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from datetime import datetime


logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle HTTP exceptions with professional error responses.
        """
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "http_error"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle validation errors with detailed field-level error messages.
        """
        logger.warning(f"Validation error - Path: {request.url.path} - Errors: {exc.errors()}")
        
        # Format validation errors for better client understanding
        formatted_errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Validation failed",
                    "type": "validation_error",
                    "details": formatted_errors
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handle unexpected server errors with proper logging and user-friendly messages.
        """
        logger.error(f"Unexpected error - Path: {request.url.path} - Error: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Don't expose internal error details to users in production
        error_message = "An unexpected error occurred. Please try again later."
        
        # In development, you might want to see the actual error
        if app.debug:
            error_message = str(exc)
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": error_message,
                    "type": "server_error"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            },
        )
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Log all requests for monitoring and debugging.
        """
        start_time = datetime.utcnow()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            # Log failed requests
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"{request.method} {request.url.path} - ERROR - {duration:.3f}s - {str(e)}")
            raise
