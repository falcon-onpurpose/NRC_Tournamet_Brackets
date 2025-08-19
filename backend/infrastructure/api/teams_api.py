"""
Teams API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import (
    TeamCreate, TeamUpdate, TeamResponse, BaseResponse
)

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new team."""
    try:
        service = factory.create_team_service()
        team = await service.create_team(team_data)
        return team
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    name: Optional[str] = Query(None, description="Filter by team name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """List teams with optional filters."""
    try:
        service = factory.create_team_service()
        filters = {}
        if tournament_id:
            filters['tournament_id'] = tournament_id
        if name:
            filters['name'] = name
        if email:
            filters['email'] = email
        
        teams = await service.get_teams(**filters)
        return teams
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get team by ID."""
    try:
        service = factory.create_team_service()
        team = await service.get_team(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Update team."""
    try:
        service = factory.create_team_service()
        team = await service.update_team(team_id, team_data)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{team_id}", response_model=BaseResponse)
async def delete_team(
    team_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete team."""
    try:
        service = factory.create_team_service()
        success = await service.delete_team(team_id)
        if success:
            return BaseResponse(message=f"Team {team_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tournament/{tournament_id}", response_model=List[TeamResponse])
async def get_teams_by_tournament(
    tournament_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get all teams for a tournament."""
    try:
        service = factory.create_team_service()
        teams = await service.get_teams_by_tournament(tournament_id)
        return teams
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
