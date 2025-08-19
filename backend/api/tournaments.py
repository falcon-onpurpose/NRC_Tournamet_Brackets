"""
Tournament API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from database import get_session
from services.container import Container, get_container
from services.tournament_service import TournamentService
from schemas import (
    TournamentCreate, TournamentUpdate, TournamentResponse,
    BaseResponse
)

router = APIRouter()


def get_tournament_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
) -> TournamentService:
    """Get tournament service with database session."""
    return container.get_tournament_service_with_session(session)


@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    tournament_data: TournamentCreate,
    service: TournamentService = Depends(get_tournament_service)
):
    """Create a new tournament."""
    try:
        tournament = await service.create_tournament(tournament_data)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
    status_filter: Optional[str] = Query(None, description="Filter by tournament status"),
    format_filter: Optional[str] = Query(None, description="Filter by tournament format"),
    service: TournamentService = Depends(get_tournament_service)
):
    """List all tournaments with optional filters."""
    try:
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if format_filter:
            filters["format"] = format_filter
        
        tournaments = await service.get_tournaments(filters)
        return tournaments
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Get tournament by ID."""
    try:
        tournament = await service.get_tournament(tournament_id)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament_data: TournamentUpdate,
    service: TournamentService = Depends(get_tournament_service)
):
    """Update tournament."""
    try:
        tournament = await service.update_tournament(tournament_id, tournament_data)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{tournament_id}", response_model=BaseResponse)
async def delete_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Delete tournament."""
    try:
        success = await service.delete_tournament(tournament_id)
        if success:
            return BaseResponse(message=f"Tournament {tournament_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete active tournament")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{tournament_id}/start", response_model=TournamentResponse)
async def start_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Start a tournament."""
    try:
        tournament = await service.start_tournament(tournament_id)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{tournament_id}/pause", response_model=TournamentResponse)
async def pause_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Pause a tournament."""
    try:
        tournament = await service.pause_tournament(tournament_id)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{tournament_id}/resume", response_model=TournamentResponse)
async def resume_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Resume a tournament."""
    try:
        tournament = await service.resume_tournament(tournament_id)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{tournament_id}/complete", response_model=TournamentResponse)
async def complete_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Complete a tournament."""
    try:
        tournament = await service.complete_tournament(tournament_id)
        return tournament
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{tournament_id}/stats")
async def get_tournament_stats(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Get tournament statistics."""
    try:
        stats = await service.get_tournament_stats(tournament_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
