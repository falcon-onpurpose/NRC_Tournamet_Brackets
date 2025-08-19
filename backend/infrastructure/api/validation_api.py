"""
Validation API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import (
    TournamentCreate, TournamentUpdate, SwissMatchCreate, EliminationMatchCreate,
    TeamCreate, TeamUpdate, RobotCreate, RobotUpdate, PlayerCreate, PlayerUpdate
)

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/tournament")
async def validate_tournament_data(
    tournament_data: TournamentCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate tournament creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_tournament_data(tournament_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "tournament_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/tournament/update")
async def validate_tournament_update_data(
    tournament_data: TournamentUpdate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate tournament update data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_tournament_update(tournament_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "tournament_update"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/team")
async def validate_team_data(
    team_data: TeamCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate team creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_team_data(team_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "team_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/match/swiss")
async def validate_swiss_match_data(
    match_data: SwissMatchCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate Swiss match creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_match_data(match_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "swiss_match_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/match/elimination")
async def validate_elimination_match_data(
    match_data: EliminationMatchCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate elimination match creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_elimination_match_data(match_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "elimination_match_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/robot")
async def validate_robot_data(
    robot_data: RobotCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate robot creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_robot_data(robot_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "robot_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/player")
async def validate_player_data(
    player_data: PlayerCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate player creation data."""
    try:
        service = factory.create_validation_service()
        result = service.validate_player_data(player_data)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "player_creation"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/csv")
async def validate_csv_data(
    csv_data: Dict[str, Any],
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate CSV import data."""
    try:
        service = factory.create_validation_service()
        
        # Extract CSV data from request
        csv_content = csv_data.get("csv_content", "")
        result = service.validate_csv_import_data(csv_content)
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "validation_type": "csv_import"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
