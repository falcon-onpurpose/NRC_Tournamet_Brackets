"""
Temporary main file for testing refactored structure.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Optional

from config import get_settings
from database import get_session, create_db_and_tables
from infrastructure.api.teams_api import router as teams_router
from infrastructure.api.matches_api import router as matches_router
from infrastructure.api.validation_api import router as validation_router
from infrastructure.api.csv_import_api import router as csv_import_router
from infrastructure.api.robots_api import router as robots_router
from infrastructure.api.players_api import router as players_router
from infrastructure.api.robot_classes_api import router as robot_classes_router
from infrastructure.api.tournaments_api import router as tournaments_router

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
    logger.info("Starting NRC Tournament Program (Refactored)...")
    
    # Initialize database
    try:
        await create_db_and_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down NRC Tournament Program...")


# Create FastAPI application
app = FastAPI(
    title="NRC Tournament Program (Refactored)",
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
    return {"status": "healthy", "version": "1.0.0"}


# Include routers
app.include_router(
    tournaments_router,
    prefix="/api/v1/tournaments",
    tags=["Tournaments"],
)

app.include_router(
    teams_router,
    prefix="/api/v1/teams",
    tags=["Teams"],
)

app.include_router(
    matches_router,
    prefix="/api/v1/matches",
    tags=["Matches"],
)

app.include_router(
    validation_router,
    prefix="/api/v1/validation",
    tags=["Validation"],
)

app.include_router(
    csv_import_router,
    prefix="/api/v1/csv-import",
    tags=["CSV Import"],
)

app.include_router(
    robots_router,
    prefix="/api/v1/robots",
    tags=["Robots"],
)

app.include_router(
    players_router,
    prefix="/api/v1/players",
    tags=["Players"],
)

app.include_router(
    robot_classes_router,
    prefix="/api/v1/robot-classes",
    tags=["Robot Classes"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main_refactored:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
