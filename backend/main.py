"""
NRC Tournament Program - Main FastAPI Application
Based on Bracket tournament system with arena integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional

from .database import engine, create_db_and_tables
from .models import Tournament, Match, Team, Player
from .schemas import TournamentCreate, TournamentResponse, MatchCreate, MatchResponse
from .arena_integration import ArenaIntegration
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    create_db_and_tables()
    print("🚀 NRC Tournament Program started")
    yield
    # Shutdown
    print("🛑 NRC Tournament Program stopped")


app = FastAPI(
    title="NRC Tournament Program",
    description="Tournament management system with arena integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for public displays
app.mount("/static", StaticFiles(directory="static"), name="static")

# Arena integration instance
arena_integration = ArenaIntegration()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NRC Tournament Program API",
        "version": "1.0.0",
        "docs": "/docs",
        "arena_integration": "/arena/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "arena_connected": arena_integration.is_connected()}


# Tournament endpoints
@app.post("/tournaments/", response_model=TournamentResponse)
async def create_tournament(tournament: TournamentCreate):
    """Create a new tournament"""
    # Implementation will be added
    pass


@app.get("/tournaments/", response_model=List[TournamentResponse])
async def list_tournaments():
    """List all tournaments"""
    # Implementation will be added
    pass


@app.get("/tournaments/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: int):
    """Get tournament details"""
    # Implementation will be added
    pass


# Match endpoints
@app.post("/matches/", response_model=MatchResponse)
async def create_match(match: MatchCreate):
    """Create a new match"""
    # Implementation will be added
    pass


@app.get("/matches/", response_model=List[MatchResponse])
async def list_matches(tournament_id: Optional[int] = None):
    """List matches, optionally filtered by tournament"""
    # Implementation will be added
    pass


@app.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int):
    """Get match details"""
    # Implementation will be added
    pass


@app.post("/matches/{match_id}/start")
async def start_match(match_id: int):
    """Start a match and communicate with arena"""
    try:
        # Get match details
        # Send match parameters to arena
        arena_params = {
            "match_id": match_id,
            "duration": 300,  # 5 minutes default
            "pit_assignment": "pit_1"
        }
        
        success = await arena_integration.start_match(arena_params)
        if success:
            return {"message": f"Match {match_id} started", "arena_status": "ready"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start match in arena")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/matches/{match_id}/complete")
async def complete_match(match_id: int, winner_id: int, scores: dict):
    """Complete a match and update tournament"""
    try:
        # Update match results
        # Update tournament brackets
        # Report completion to arena
        await arena_integration.complete_match(match_id, winner_id, scores)
        return {"message": f"Match {match_id} completed", "winner_id": winner_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Public display endpoints
@app.get("/public/tournaments/{tournament_id}")
async def public_tournament_view(tournament_id: int):
    """Public view of tournament for displays"""
    # Implementation will be added
    pass


@app.get("/public/matches/upcoming")
async def upcoming_matches():
    """Get upcoming matches for public displays"""
    # Implementation will be added
    pass


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
