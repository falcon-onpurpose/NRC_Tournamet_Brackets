"""
Matches API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from database import get_session
from services.container import Container, get_container
from services.match_service import MatchService
from schemas import (
    SwissMatchCreate, SwissMatchUpdate, SwissMatchResponse,
    EliminationMatchCreate, EliminationMatchUpdate, EliminationMatchResponse,
    MatchResultCreate, BaseResponse
)

router = APIRouter()


def get_match_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
) -> MatchService:
    """Get match service with database session."""
    return container.get_match_service_with_session(session)


# Swiss match endpoints
@router.post("/swiss", response_model=SwissMatchResponse, status_code=status.HTTP_201_CREATED)
async def create_swiss_match(
    match_data: SwissMatchCreate,
    service: MatchService = Depends(get_match_service)
):
    """Create a new Swiss match."""
    try:
        match = await service.create_swiss_match(match_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/swiss", response_model=List[SwissMatchResponse])
async def list_swiss_matches(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    round_number: Optional[int] = Query(None, description="Filter by round number"),
    status_filter: Optional[str] = Query(None, description="Filter by match status"),
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """List Swiss matches with optional filters."""
    try:
        matches = await service.get_swiss_matches(session, tournament_id, round_number, status_filter)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/swiss/{match_id}", response_model=SwissMatchResponse)
async def get_swiss_match(
    match_id: int,
    service: MatchService = Depends(get_match_service)
):
    """Get Swiss match by ID."""
    try:
        match = await service.get_swiss_match(match_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/swiss/{match_id}", response_model=SwissMatchResponse)
async def update_swiss_match(
    match_id: int,
    match_data: SwissMatchUpdate,
    service: MatchService = Depends(get_match_service)
):
    """Update Swiss match."""
    try:
        match = await service.update_swiss_match(match_id, match_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/swiss/{match_id}/start", response_model=SwissMatchResponse)
async def start_swiss_match(
    match_id: int,
    service: MatchService = Depends(get_match_service)
):
    """Start a Swiss match."""
    try:
        match = await service.start_swiss_match(match_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/swiss/{match_id}/complete", response_model=SwissMatchResponse)
async def complete_swiss_match(
    match_id: int,
    result_data: MatchResultCreate,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Complete a Swiss match with results."""
    try:
        match = await service.complete_swiss_match(session, match_id, result_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Elimination match endpoints
@router.post("/elimination", response_model=EliminationMatchResponse, status_code=status.HTTP_201_CREATED)
async def create_elimination_match(
    match_data: EliminationMatchCreate,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Create a new elimination match."""
    try:
        match = await service.create_elimination_match(session, match_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/elimination", response_model=List[EliminationMatchResponse])
async def list_elimination_matches(
    bracket_id: Optional[int] = Query(None, description="Filter by bracket ID"),
    round_number: Optional[int] = Query(None, description="Filter by round number"),
    status_filter: Optional[str] = Query(None, description="Filter by match status"),
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """List elimination matches with optional filters."""
    try:
        matches = await service.get_elimination_matches(session, bracket_id, round_number, status_filter)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/elimination/{match_id}", response_model=EliminationMatchResponse)
async def get_elimination_match(
    match_id: int,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Get elimination match by ID."""
    try:
        match = await service.get_elimination_match(session, match_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/elimination/{match_id}", response_model=EliminationMatchResponse)
async def update_elimination_match(
    match_id: int,
    match_data: EliminationMatchUpdate,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Update elimination match."""
    try:
        match = await service.update_elimination_match(session, match_id, match_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/elimination/{match_id}/start", response_model=EliminationMatchResponse)
async def start_elimination_match(
    match_id: int,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Start an elimination match."""
    try:
        match = await service.start_elimination_match(session, match_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/elimination/{match_id}/complete", response_model=EliminationMatchResponse)
async def complete_elimination_match(
    match_id: int,
    result_data: MatchResultCreate,
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Complete an elimination match with results."""
    try:
        match = await service.complete_elimination_match(session, match_id, result_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# General match endpoints
@router.get("/pending", response_model=List[Dict[str, Any]])
async def get_pending_matches(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Get pending matches for a tournament."""
    try:
        matches = await service.get_pending_matches(session, tournament_id)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics")
async def get_match_statistics(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    service: MatchService = Depends(get_match_service),
    session: AsyncSession = Depends(get_session)
):
    """Get match statistics for a tournament."""
    try:
        stats = await service.get_match_statistics(session, tournament_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
