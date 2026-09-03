"""PEEXH FastAPI backend entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.speech_ws import router as speech_ws_router
from app.core.config import settings

app = FastAPI(
    title="PEEXH Backend API",
    description="Assistive communication voice agent backend for people with dysarthria.",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(speech_ws_router)



@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "app": settings.APP_NAME,
        "description": "PEEXH Voice Agent Backend",
        "docs_url": "/docs",
        "health_url": "/health",
    }
