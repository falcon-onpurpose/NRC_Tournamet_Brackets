"""
Robot Classes API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from services.container import Container, get_container
from services.team_service import TeamService
from schemas import (
    RobotClassCreate, RobotClassUpdate, RobotClassResponse,
    BaseResponse
)

router = APIRouter()


def get_team_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
) -> TeamService:
    """Get team service with database session."""
    return container.get_team_service_with_session(session)


@router.post("/", response_model=RobotClassResponse, status_code=status.HTTP_201_CREATED)
async def create_robot_class(
    robot_class_data: RobotClassCreate,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Create a new robot class."""
    try:
        robot_class = await service.create_robot_class(session, robot_class_data)
        return robot_class
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[RobotClassResponse])
async def list_robot_classes(
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """List all robot classes."""
    try:
        robot_classes = await service.get_robot_classes(session)
        return robot_classes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{robot_class_id}", response_model=RobotClassResponse)
async def get_robot_class(
    robot_class_id: int,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Get robot class by ID."""
    try:
        robot_class = await service.get_robot_class(session, robot_class_id)
        if robot_class is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return robot_class
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{robot_class_id}", response_model=RobotClassResponse)
async def update_robot_class(
    robot_class_id: int,
    robot_class_data: RobotClassUpdate,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Update robot class."""
    try:
        robot_class = await service.update_robot_class(session, robot_class_id, robot_class_data)
        if robot_class is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return robot_class
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{robot_class_id}", response_model=BaseResponse)
async def delete_robot_class(
    robot_class_id: int,
    service: TeamService = Depends(get_team_service),
    session: AsyncSession = Depends(get_session)
):
    """Delete robot class."""
    try:
        success = await service.delete_robot_class(session, robot_class_id)
        if success:
            return BaseResponse(message=f"Robot class {robot_class_id} deleted successfully")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete robot class with active robots")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
