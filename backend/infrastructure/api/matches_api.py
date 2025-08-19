"""
Matches API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import (
    SwissMatchCreate, SwissMatchResponse, EliminationMatchCreate, EliminationMatchResponse,
    MatchResultCreate, MatchStatisticsResponse, BaseResponse
)

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


# Swiss Match Endpoints
@router.post("/swiss", response_model=SwissMatchResponse, status_code=status.HTTP_201_CREATED)
async def create_swiss_match(
    match_data: SwissMatchCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new Swiss match."""
    try:
        service = factory.create_match_service()
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
    status: Optional[str] = Query(None, description="Filter by match status"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """List Swiss matches with optional filters."""
    try:
        service = factory.create_match_service()
        filters = {}
        if tournament_id:
            filters['tournament_id'] = tournament_id
        if round_number:
            filters['round_number'] = round_number
        if status:
            filters['status'] = status
        
        matches = await service.get_swiss_matches(**filters)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/swiss/{match_id}", response_model=SwissMatchResponse)
async def get_swiss_match(
    match_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get Swiss match by ID."""
    try:
        service = factory.create_match_service()
        match = await service.get_swiss_match(match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swiss match not found")
        return match
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/swiss/{match_id}/complete", response_model=SwissMatchResponse)
async def complete_swiss_match(
    match_id: int,
    result_data: MatchResultCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Complete a Swiss match with results."""
    try:
        service = factory.create_match_service()
        match = await service.complete_swiss_match(match_id, result_data)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swiss match not found")
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Elimination Match Endpoints
@router.post("/elimination", response_model=EliminationMatchResponse, status_code=status.HTTP_201_CREATED)
async def create_elimination_match(
    match_data: EliminationMatchCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new elimination match."""
    try:
        service = factory.create_match_service()
        match = await service.create_elimination_match(match_data)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/elimination", response_model=List[EliminationMatchResponse])
async def list_elimination_matches(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    bracket_id: Optional[int] = Query(None, description="Filter by bracket ID"),
    round_number: Optional[int] = Query(None, description="Filter by round number"),
    status: Optional[str] = Query(None, description="Filter by match status"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """List elimination matches with optional filters."""
    try:
        service = factory.create_match_service()
        filters = {}
        if tournament_id:
            filters['tournament_id'] = tournament_id
        if bracket_id:
            filters['bracket_id'] = bracket_id
        if round_number:
            filters['round_number'] = round_number
        if status:
            filters['status'] = status
        
        matches = await service.get_elimination_matches(**filters)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/elimination/{match_id}", response_model=EliminationMatchResponse)
async def get_elimination_match(
    match_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get elimination match by ID."""
    try:
        service = factory.create_match_service()
        match = await service.get_elimination_match(match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elimination match not found")
        return match
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/elimination/{match_id}", response_model=EliminationMatchResponse)
async def update_elimination_match(
    match_id: int,
    match_data: EliminationMatchCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Update an elimination match."""
    try:
        service = factory.create_match_service()
        match = await service.update_elimination_match(match_id, match_data)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elimination match not found")
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/elimination/{match_id}/start", response_model=EliminationMatchResponse)
async def start_elimination_match(
    match_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Start an elimination match."""
    try:
        service = factory.create_match_service()
        match = await service.start_elimination_match(match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elimination match not found")
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/elimination/{match_id}/complete", response_model=EliminationMatchResponse)
async def complete_elimination_match(
    match_id: int,
    result_data: MatchResultCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Complete an elimination match with results."""
    try:
        service = factory.create_match_service()
        match = await service.complete_elimination_match(match_id, result_data)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elimination match not found")
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# General Match Endpoints
@router.get("/pending", response_model=List[dict])
async def get_pending_matches(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get pending matches for a tournament."""
    try:
        service = factory.create_match_service()
        matches = await service.get_pending_matches(tournament_id)
        return matches
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics", response_model=MatchStatisticsResponse)
async def get_match_statistics(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get match statistics."""
    try:
        service = factory.create_match_service()
        stats = await service.get_match_statistics(tournament_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{match_id}", response_model=BaseResponse)
async def delete_match(
    match_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete a match (Swiss or elimination)."""
    try:
        service = factory.create_match_service()
        success = await service.delete_match(match_id)
        if success:
            return BaseResponse(message=f"Match {match_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
