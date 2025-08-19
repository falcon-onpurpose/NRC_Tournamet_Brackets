"""
Public Display API endpoints for view-only tournament information.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from database import get_session
from services.container import Container, get_container
from services.tournament_service import TournamentService
from services.match_service import MatchService
from services.standings_service import StandingsService
from services.bracket_service import BracketService
from schemas import BaseResponse

router = APIRouter()


def get_tournament_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
):
    """Get tournament service with database session."""
    return container.get_tournament_service_with_session(session)


def get_match_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
):
    """Get match service with database session."""
    return container.get_match_service_with_session(session)


def get_standings_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
):
    """Get standings service with database session."""
    return container.get_standings_service_with_session(session)


def get_bracket_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
):
    """Get bracket service with database session."""
    return container.get_bracket_service_with_session(session)


@router.get("/current-match")
async def get_current_match(
    tournament_id: Optional[int] = Query(None, description="Tournament ID"),
    service: MatchService = Depends(get_match_service)
):
    """Get the currently active match for public display."""
    try:
        # Get the most recent in-progress match
        matches = await service.get_pending_matches(tournament_id)
        current_match = None
        
        for match in matches:
            if match.get("status") == "in_progress":
                current_match = match
                break
        
        if not current_match:
            # Get the next scheduled match
            for match in matches:
                if match.get("status") == "scheduled":
                    current_match = match
                    break
        
        if not current_match:
            return {
                "current_match": None,
                "message": "No active or upcoming matches"
            }
        
        return {
            "current_match": current_match,
            "estimated_start_time": current_match.get("estimated_start_time"),
            "match_number": current_match.get("match_number"),
            "round_number": current_match.get("round_number")
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/upcoming-matches")
async def get_upcoming_matches(
    tournament_id: Optional[int] = Query(None, description="Tournament ID"),
    limit: int = Query(5, description="Number of upcoming matches to return"),
    service: MatchService = Depends(get_match_service)
):
    """Get upcoming matches for public display."""
    try:
        matches = await service.get_pending_matches(tournament_id)
        
        # Filter for scheduled matches and limit results
        upcoming_matches = [
            match for match in matches 
            if match.get("status") == "scheduled"
        ][:limit]
        
        return {
            "upcoming_matches": upcoming_matches,
            "count": len(upcoming_matches)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/standings")
async def get_public_standings(
    tournament_id: int = Query(..., description="Tournament ID"),
    service: StandingsService = Depends(get_standings_service)
):
    """Get tournament standings for public display."""
    try:
        standings = await service.get_tournament_standings(tournament_id)
        return standings
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/brackets")
async def get_public_brackets(
    tournament_id: int = Query(..., description="Tournament ID"),
    bracket_type: Optional[str] = Query(None, description="Bracket type (winners/losers)"),
    service: BracketService = Depends(get_bracket_service)
):
    """Get tournament brackets for public display."""
    try:
        matches = await service.get_bracket_matches(tournament_id, bracket_type)
        
        # Group matches by round for bracket display
        brackets = {}
        for match in matches:
            round_num = match.round_number
            if round_num not in brackets:
                brackets[round_num] = []
            brackets[round_num].append(match)
        
        return {
            "tournament_id": tournament_id,
            "bracket_type": bracket_type or "all",
            "brackets": brackets
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tournament-info")
async def get_tournament_info(
    tournament_id: int = Query(..., description="Tournament ID"),
    service: TournamentService = Depends(get_tournament_service)
):
    """Get basic tournament information for public display."""
    try:
        tournament = await service.get_tournament(tournament_id)
        stats = await service.get_tournament_stats(tournament_id)
        
        return {
            "tournament": {
                "id": tournament.id,
                "name": tournament.name,
                "format": tournament.format,
                "status": tournament.status,
                "location": tournament.location,
                "start_date": tournament.start_date,
                "end_date": tournament.end_date
            },
            "statistics": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/active-tournaments")
async def get_active_tournaments(
    service: TournamentService = Depends(get_tournament_service)
):
    """Get list of active tournaments for public display."""
    try:
        tournaments = await service.get_tournaments({"status": "active"})
        
        return {
            "active_tournaments": [
                {
                    "id": t.id,
                    "name": t.name,
                    "format": t.format,
                    "location": t.location,
                    "team_count": getattr(t, 'team_count', 0)
                }
                for t in tournaments
            ],
            "count": len(tournaments)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
