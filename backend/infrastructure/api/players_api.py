"""
Player API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import PlayerCreate, PlayerUpdate, PlayerResponse

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player: PlayerCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new player."""
    try:
        service = factory.create_player_service()
        created_player = await service.create_player(player)
        return created_player
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[PlayerResponse])
async def get_players(
    team_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get players with optional filters."""
    try:
        service = factory.create_player_service()
        
        filters = {}
        if team_id is not None:
            filters["team_id"] = team_id
        if first_name:
            filters["first_name"] = first_name
        if last_name:
            filters["last_name"] = last_name
        if email:
            filters["email"] = email
        
        players = await service.get_players(**filters)
        return players
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get player by ID."""
    try:
        service = factory.create_player_service()
        player = await service.get_player(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        return player
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Update player."""
    try:
        service = factory.create_player_service()
        updated_player = await service.update_player(player_id, player_update)
        if not updated_player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        return updated_player
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{player_id}")
async def delete_player(
    player_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete player."""
    try:
        service = factory.create_player_service()
        deleted = await service.delete_player(player_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        return {"message": "Player deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/team/{team_id}", response_model=List[PlayerResponse])
async def get_players_by_team(
    team_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get all players for a specific team."""
    try:
        service = factory.create_player_service()
        players = await service.get_players_by_team(team_id)
        return players
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/{search_term}", response_model=List[PlayerResponse])
async def search_players(
    search_term: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Search players by name."""
    try:
        service = factory.create_player_service()
        players = await service.search_players(search_term)
        return players
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/email/{email}", response_model=List[PlayerResponse])
async def get_players_by_email(
    email: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Find players by email address."""
    try:
        service = factory.create_player_service()
        players = await service.find_players_by_email(email)
        return players
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary")
async def get_player_statistics(
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get player statistics."""
    try:
        service = factory.create_player_service()
        stats = await service.get_player_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
