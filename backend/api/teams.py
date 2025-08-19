"""
Teams API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from services.container import Container, get_container
from services.team_service import TeamService
from schemas import (
    TeamCreate, TeamUpdate, TeamResponse,
    RobotCreate, RobotUpdate, RobotResponse,
    PlayerCreate, PlayerUpdate, PlayerResponse,
    BaseResponse
)

router = APIRouter()


def get_team_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
) -> TeamService:
    """Get team service with database session."""
    return container.get_team_service_with_session(session)


# Team endpoints
@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Create a new team."""
    try:
        team = await service.create_team(session, team_data)
        return team
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """List teams with optional tournament filter."""
    try:
        teams = await service.get_teams(session, tournament_id)
        return teams
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Get team by ID."""
    try:
        team = await service.get_team(session, team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Update team."""
    try:
        team = await service.update_team(session, team_id, team_data)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{team_id}", response_model=BaseResponse)
async def delete_team(
    team_id: int,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Delete team."""
    try:
        success = await service.delete_team(session, team_id)
        if success:
            return BaseResponse(message=f"Team {team_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete team with active matches")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Robot endpoints
@router.post("/{team_id}/robots", response_model=RobotResponse, status_code=status.HTTP_201_CREATED)
async def create_robot(
    team_id: int,
    robot_data: RobotCreate,
    service: TeamService = Depends(get_team_service)
):
    """Create a new robot for a team."""
    try:
        robot = await service.create_robot(team_id, robot_data)
        return robot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{team_id}/robots", response_model=List[RobotResponse])
async def list_team_robots(
    team_id: int,
    service: TeamService = Depends(get_team_service)
):
    """List robots for a team."""
    try:
        robots = await service.get_team_robots(team_id)
        return robots
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/robots/{robot_id}", response_model=RobotResponse)
async def get_robot(
    robot_id: int,
    service: TeamService = Depends(get_team_service)
):
    """Get robot by ID."""
    try:
        robot = await service.get_robot(robot_id)
        return robot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/robots/{robot_id}", response_model=RobotResponse)
async def update_robot(
    robot_id: int,
    robot_data: RobotUpdate,
    service: TeamService = Depends(get_team_service)
):
    """Update robot."""
    try:
        robot = await service.update_robot(robot_id, robot_data)
        return robot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/robots/{robot_id}", response_model=BaseResponse)
async def delete_robot(
    robot_id: int,
    service: TeamService = Depends(get_team_service)
):
    """Delete robot."""
    try:
        success = await service.delete_robot(robot_id)
        if success:
            return BaseResponse(message=f"Robot {robot_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete robot with active matches")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Player endpoints
@router.post("/{team_id}/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    team_id: int,
    player_data: PlayerCreate,
    service: TeamService = Depends(get_team_service)
):
    """Create a new player for a team."""
    try:
        player = await service.create_player(team_id, player_data)
        return player
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{team_id}/players", response_model=List[PlayerResponse])
async def list_team_players(
    team_id: int,
    service: TeamService = Depends(get_team_service)
):
    """List players for a team."""
    try:
        players = await service.get_team_players(team_id)
        return players
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    service: TeamService = Depends(get_team_service)
):
    """Get player by ID."""
    try:
        player = await service.get_player(player_id)
        return player
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/players/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    service: TeamService = Depends(get_team_service)
):
    """Update player."""
    try:
        player = await service.update_player(player_id, player_data)
        return player
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/players/{player_id}", response_model=BaseResponse)
async def delete_player(
    player_id: int,
    service: TeamService = Depends(get_team_service)
):
    """Delete player."""
    try:
        success = await service.delete_player(player_id)
        if success:
            return BaseResponse(message=f"Player {player_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete player")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
