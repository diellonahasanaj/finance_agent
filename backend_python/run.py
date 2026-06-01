#!/usr/bin/env python3
"""
Startup script for Personal Finance Agent Backend
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.core.app:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=True,
        log_level="info"
    )
