"""
Tournaments API router for tournament management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from domain.tournament.tournament_service import TournamentService
from domain.tournament.tournament_validator import TournamentValidator
from schemas import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentListResponse,
    SuccessResponse,
    ErrorResponse
)

router = APIRouter()

@router.get("/", response_model=List[TournamentResponse])
async def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get all tournaments with optional filtering."""
    try:
        service = TournamentService()
        tournaments = await service.get_tournaments(
            session=session,
            skip=skip,
            limit=limit,
            status=status
        )
        return tournaments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tournaments: {str(e)}"
        )

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific tournament by ID."""
    try:
        service = TournamentService()
        tournament = await service.get_tournament(session=session, tournament_id=tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found"
            )
        return tournament
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tournament: {str(e)}"
        )

@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament_data: TournamentCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new tournament."""
    try:
        # Validate tournament data
        validator = TournamentValidator()
        validation_result = await validator.validate_tournament_create(tournament_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result.errors
            )
        
        # Create tournament
        service = TournamentService()
        tournament = await service.create_tournament(
            session=session,
            tournament_data=tournament_data
        )
        return tournament
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tournament: {str(e)}"
        )

@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament_data: TournamentUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an existing tournament."""
    try:
        # Validate tournament data
        validator = TournamentValidator()
        validation_result = await validator.validate_tournament_update(tournament_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result.errors
            )
        
        # Update tournament
        service = TournamentService()
        tournament = await service.update_tournament(
            session=session,
            tournament_id=tournament_id,
            tournament_data=tournament_data
        )
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found"
            )
        return tournament
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tournament: {str(e)}"
        )

@router.delete("/{tournament_id}", response_model=SuccessResponse)
async def delete_tournament(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a tournament."""
    try:
        service = TournamentService()
        success = await service.delete_tournament(
            session=session,
            tournament_id=tournament_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found"
            )
        return {"success": True, "message": "Tournament deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tournament: {str(e)}"
        )

@router.get("/{tournament_id}/teams", response_model=List[dict])
async def get_tournament_teams(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all teams for a specific tournament."""
    try:
        service = TournamentService()
        teams = await service.get_tournament_teams(
            session=session,
            tournament_id=tournament_id
        )
        return teams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tournament teams: {str(e)}"
        )

@router.get("/{tournament_id}/matches", response_model=List[dict])
async def get_tournament_matches(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all matches for a specific tournament."""
    try:
        service = TournamentService()
        matches = await service.get_tournament_matches(
            session=session,
            tournament_id=tournament_id
        )
        return matches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tournament matches: {str(e)}"
        )

@router.post("/{tournament_id}/start", response_model=SuccessResponse)
async def start_tournament(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Start a tournament."""
    try:
        service = TournamentService()
        success = await service.start_tournament(
            session=session,
            tournament_id=tournament_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start tournament"
            )
        return {"success": True, "message": "Tournament started successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start tournament: {str(e)}"
        )

@router.post("/{tournament_id}/end", response_model=SuccessResponse)
async def end_tournament(
    tournament_id: int,
    session: AsyncSession = Depends(get_session)
):
    """End a tournament."""
    try:
        service = TournamentService()
        success = await service.end_tournament(
            session=session,
            tournament_id=tournament_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to end tournament"
            )
        return {"success": True, "message": "Tournament ended successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end tournament: {str(e)}"
        )
