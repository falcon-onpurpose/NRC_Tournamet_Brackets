"""
Main FastAPI application for NRC Tournament Program.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Optional

from config import get_settings
from database import get_session, create_db_and_tables
from services.container import get_container, Container
from api import tournaments, teams, matches, robot_classes, public, arena


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting NRC Tournament Program...")
    
    # Initialize database
    try:
        await create_db_and_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize services container
    container = get_container()
    logger.info("Services container initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NRC Tournament Program...")


# Create FastAPI application
app = FastAPI(
    title="NRC Tournament Program",
    description="Tournament management system for robot combat events",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security (optional)
# if hasattr(settings, 'TRUSTED_HOSTS') and settings.TRUSTED_HOSTS:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=settings.TRUSTED_HOSTS
#     )


# Dependency injection
def get_container_dependency() -> Container:
    """Get services container dependency."""
    return get_container()


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NRC Tournament Program",
        "version": "1.0.0"
    }


# Include API routers
app.include_router(
    tournaments.router,
    prefix="/api/v1/tournaments",
    tags=["Tournaments"],
    dependencies=[Depends(get_container_dependency)]
)

app.include_router(
    teams.router,
    prefix="/api/v1/teams",
    tags=["Teams"],
    dependencies=[Depends(get_container_dependency)]
)

app.include_router(
    matches.router,
    prefix="/api/v1/matches",
    tags=["Matches"],
    dependencies=[Depends(get_container_dependency)]
)

app.include_router(
    robot_classes.router,
    prefix="/api/v1/robot-classes",
    tags=["Robot Classes"],
    dependencies=[Depends(get_container_dependency)]
)

app.include_router(
    public.router,
    prefix="/api/v1/public",
    tags=["Public Display"],
    dependencies=[Depends(get_container_dependency)]
)

app.include_router(
    arena.router,
    prefix="/api/v1/arena",
    tags=["Arena Integration"],
    dependencies=[Depends(get_container_dependency)]
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
